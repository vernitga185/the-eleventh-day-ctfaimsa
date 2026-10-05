import os
import hashlib
import json
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from argon2.low_level import hash_secret_raw, Type
import unicodedata

def normalize_verse(verse: str) -> str:
    verse = unicodedata.normalize('NFC', verse)
    verse = ' '.join(verse.split())
    return verse.strip()

def derive_plate_key(verse_a: str, verse_b: str, digest: str, salt: bytes) -> bytes:
    norm_a = normalize_verse(verse_a)
    norm_b = normalize_verse(verse_b)
    
    key_material = norm_a.encode('utf-8') + norm_b.encode('utf-8') + digest.encode('utf-8') + salt
    
    return hash_secret_raw(
        secret=key_material,
        salt=salt,
        time_cost=3,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        type=Type.ID
    )

def encrypt_plate_data(key: bytes, nonce: bytes, plaintext: bytes, aad: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.encrypt(nonce, plaintext, aad)

def derive_final_key(partial_a: str, digest_b: str, salt_f: bytes, team_id: str) -> bytes:
    key_material = partial_a.encode('utf-8') + digest_b.encode('utf-8') + salt_f + team_id.encode('utf-8')
    return hash_secret_raw(
        secret=key_material,
        salt=salt_f,
        time_cost=3,
        memory_cost=65536,
        parallelism=1,
        hash_len=32,
        type=Type.ID
    )

def decrypt_final_data(key: bytes, ciphertext: bytes, nonce: bytes, aad: bytes) -> bytes:
    aesgcm = AESGCM(key)
    return aesgcm.decrypt(nonce, ciphertext, aad)
