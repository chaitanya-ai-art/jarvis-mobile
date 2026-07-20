from __future__ import annotations

import ipaddress
import socket
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

BASE = Path(__file__).resolve().parent
CERT_DIR = BASE / "certs"
CA_KEY = CERT_DIR / "jarvis-ca-key.pem"
CA_CERT = CERT_DIR / "jarvis-ca.crt"
SERVER_KEY = CERT_DIR / "jarvis-server-key.pem"
SERVER_CERT = CERT_DIR / "jarvis-server.crt"


def local_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return str(sock.getsockname()[0])
    except OSError:
        return "127.0.0.1"
    finally:
        sock.close()


def write_private_key(path: Path, key: rsa.RSAPrivateKey) -> None:
    path.write_bytes(
        key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.TraditionalOpenSSL,
            serialization.NoEncryption(),
        )
    )


def ensure_certificates() -> tuple[Path, Path, Path]:
    CERT_DIR.mkdir(parents=True, exist_ok=True)
    ip = local_ip()
    now = datetime.now(timezone.utc)

    if not CA_KEY.exists() or not CA_CERT.exists():
        ca_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        ca_name = x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, "Jarvis Local CA"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Jarvis"),
        ])
        ca_cert = (
            x509.CertificateBuilder()
            .subject_name(ca_name)
            .issuer_name(ca_name)
            .public_key(ca_key.public_key())
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(days=1))
            .not_valid_after(now + timedelta(days=3650))
            .add_extension(x509.BasicConstraints(ca=True, path_length=None), critical=True)
            .add_extension(x509.KeyUsage(
                digital_signature=True, key_encipherment=False, content_commitment=False,
                data_encipherment=False, key_agreement=False, key_cert_sign=True,
                crl_sign=True, encipher_only=False, decipher_only=False,
            ), critical=True)
            .sign(ca_key, hashes.SHA256())
        )
        write_private_key(CA_KEY, ca_key)
        CA_CERT.write_bytes(ca_cert.public_bytes(serialization.Encoding.PEM))
    else:
        ca_key = serialization.load_pem_private_key(CA_KEY.read_bytes(), password=None)
        ca_cert = x509.load_pem_x509_certificate(CA_CERT.read_bytes())

    server_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, ip),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Jarvis"),
    ])
    sans = [x509.DNSName("localhost"), x509.IPAddress(ipaddress.ip_address("127.0.0.1"))]
    try:
        sans.append(x509.IPAddress(ipaddress.ip_address(ip)))
    except ValueError:
        pass

    server_cert = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(ca_cert.subject)
        .public_key(server_key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - timedelta(days=1))
        .not_valid_after(now + timedelta(days=825))
        .add_extension(x509.SubjectAlternativeName(sans), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .add_extension(x509.ExtendedKeyUsage([x509.oid.ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
        .sign(ca_key, hashes.SHA256())
    )
    write_private_key(SERVER_KEY, server_key)
    SERVER_CERT.write_bytes(server_cert.public_bytes(serialization.Encoding.PEM))
    return SERVER_CERT, SERVER_KEY, CA_CERT


if __name__ == "__main__":
    cert, key, ca = ensure_certificates()
    print(f"Server certificate: {cert}")
    print(f"Server key:         {key}")
    print(f"Phone CA file:      {ca}")
