import argparse
import os
import logging
import requests
import re
import time
import sys
from typing import List, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN")
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN")


def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.error("SUPABASE_URL e SUPABASE_KEY são obrigatórios no .env")
        raise ValueError("SUPABASE_URL e SUPABASE_KEY são obrigatórios no .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def fetch_contacts(supabase: Client, limit: int = 3) -> List[dict]:
    logger.info("Buscando contatos no Supabase...")
    try:
        response = (
            supabase.table("contacts")
            .select("name, phone")
            .limit(limit)
            .execute()
        )
    except Exception as exc:
        logger.exception("Erro ao consultar Supabase: %s", exc)
        return []

    # supabase-py returns an object with .data and .error
    data = getattr(response, "data", None)
    error = getattr(response, "error", None)
    if error:
        logger.error("Supabase retornou erro: %s", error)
        return []

    if not isinstance(data, list):
        logger.warning("Resposta inesperada do Supabase, retornando lista vazia")
        return []

    logger.info("%d contato(s) encontrado(s).", len(data))
    return data


def normalize_phone(phone: str) -> Optional[str]:
    digits = re.sub(r"\D", "", phone or "")
    if not digits:
        return None
    # If number seems local without country, assume Brazil (55)
    if len(digits) <= 11 and not digits.startswith("55"):
        digits = "55" + digits
    # basic validation: must be at least 11+ country code (13?) — accept >= 11
    if len(digits) < 11:
        return None
    return digits


def send_whatsapp_message(phone: str, name: str, dry_run: bool = False, attempts: int = 3) -> bool:
    if not all([ZAPI_INSTANCE_ID, ZAPI_TOKEN, ZAPI_CLIENT_TOKEN]):
        logger.error("Variáveis Z-API ausentes no .env (ZAPI_INSTANCE_ID, ZAPI_TOKEN, ZAPI_CLIENT_TOKEN)")
        raise ValueError("Variáveis Z-API ausentes no .env (ZAPI_INSTANCE_ID, ZAPI_TOKEN, ZAPI_CLIENT_TOKEN)")

    url = f"https://api.z-api.io/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}/send-text"
    headers = {
        "Content-Type": "application/json",
        "Client-Token": ZAPI_CLIENT_TOKEN,
    }
    message = f"Olá, {name} tudo bem com você?"
    payload = {
        "phone": phone,
        "message": message,
    }

    if dry_run:
        logger.info("[DRY-RUN] Simulando envio para %s (%s): %s", name, phone, message)
        return True

    backoff = 1.0
    for attempt in range(1, attempts + 1):
        try:
            logger.info("Enviando mensagem para %s (%s)... (tentativa %d)", name, phone, attempt)
            response = requests.post(url, json=payload, headers=headers, timeout=15)
            if response.status_code in (200, 201):
                logger.info("✅ Mensagem enviada com sucesso para %s (%s)", name, phone)
                return True
            else:
                logger.warning(
                    "Resposta inesperada da Z-API (status=%s) para %s: %s",
                    response.status_code,
                    phone,
                    response.text,
                )
        except requests.RequestException as exc:
            logger.warning("Erro de rede ao enviar para %s (%s): %s", name, phone, exc)

        if attempt < attempts:
            logger.info("Aguardando %.1fs antes da próxima tentativa...", backoff)
            time.sleep(backoff)
            backoff *= 2

    logger.error("❌ Falha ao enviar mensagem para %s (%s) após %d tentativas", name, phone, attempts)
    return False


def main(argv: Optional[List[str]] = None):
    parser = argparse.ArgumentParser(description="Enviar mensagens via Z-API para contatos do Supabase")
    parser.add_argument("--max", type=int, default=3, help="Máximo de contatos a enviar")
    parser.add_argument("--dry-run", action="store_true", help="Não enviar mensagens; apenas simular")
    args = parser.parse_args(argv)

    logger.info("=== Iniciando envio de mensagens ===")

    try:
        supabase = get_supabase_client()
    except Exception:
        logger.error("Não foi possível criar cliente Supabase. Verifique as variáveis de ambiente.")
        sys.exit(1)

    contacts = fetch_contacts(supabase, limit=args.max)

    if not contacts:
        logger.warning("Nenhum contato encontrado. Encerrando.")
        return

    success_count = 0
    failure_count = 0

    for contact in contacts:
        name = (contact.get("name") or "").strip()
        phone_raw = (contact.get("phone") or "").strip()

        phone = normalize_phone(phone_raw)
        if not name or not phone:
            logger.warning("Contato inválido ignorado: %s", contact)
            failure_count += 1
            continue

        sent = send_whatsapp_message(phone=phone, name=name, dry_run=args.dry_run)
        if sent:
            success_count += 1
        else:
            failure_count += 1

    logger.info(
        "=== Concluído | Enviados: %d | Falhas: %d ===", success_count, failure_count
    )


if __name__ == "__main__":
    main()
