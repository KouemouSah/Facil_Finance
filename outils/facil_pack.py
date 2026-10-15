"""Outil interne des packs pays (équipe Facil).

  facil_pack.py valider  <dossier-du-pack> [--racine packs]     règles du format ; code 1 si une erreur
  facil_pack.py valider-tout [--racine packs]                     tous les packs du dépôt
  facil_pack.py signer   <dossier-du-pack> --cle <fichier.pem> --ident <nom-de-cle>
  facil_pack.py resoudre <PAYS> <AAAA-MM-JJ> [--atelier]          pack en vigueur, couches, surcharges
  facil_pack.py generer-cle <ident>                               clé Ed25519 de DÉVELOPPEMENT

La clé privée n'est JAMAIS dans le dépôt : ~/.facil/cles/<ident>.pem. La clé publique va dans
facil_moteur/packs/cles/<ident>.pub. La clé de production est un sujet d'exploitation (à part).
"""
from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

DEPOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(DEPOT))
from facil_moteur import packs  # noqa: E402


def cmd_valider(dossier: Path, racine: Path) -> int:
    anomalies = packs.valider(packs.charger(dossier), racine)
    for a in anomalies:
        print(" ", a)
    erreurs = [a for a in anomalies if a.niveau == "erreur"]
    print(f"{dossier.relative_to(racine) if dossier.is_relative_to(racine) else dossier} : "
          f"{'VALIDE' if not erreurs else f'{len(erreurs)} erreur(s)'}"
          f"{f', {len(anomalies) - len(erreurs)} avertissement(s)' if len(anomalies) > len(erreurs) else ''}")
    return 1 if erreurs else 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("commande", choices=["valider", "valider-tout", "signer", "resoudre", "generer-cle"])
    p.add_argument("args", nargs="*")
    p.add_argument("--racine", default=str(DEPOT / "packs"))
    p.add_argument("--cle"); p.add_argument("--ident"); p.add_argument("--atelier", action="store_true")
    a = p.parse_args()
    racine = Path(a.racine).resolve()

    if a.commande == "valider":
        return cmd_valider(Path(a.args[0]).resolve(), racine)
    if a.commande == "valider-tout":
        codes = [cmd_valider(m.parent, racine) for m in sorted(racine.glob("*/*/pack.yaml"))]
        return 1 if any(codes) else 0
    if a.commande == "signer":
        contenu = packs.signer(Path(a.args[0]).resolve(), Path(a.cle).read_bytes(), a.ident)
        print(f"signé : {len(contenu['empreintes'])} fichier(s), clé « {a.ident} »")
        return 0
    if a.commande == "resoudre":
        pack = packs.en_vigueur(racine, a.args[0], dt.date.fromisoformat(a.args[1]), atelier=a.atelier)
        r = packs.resoudre(racine, pack)
        print(f"pack en vigueur : {pack.ident} (statut {pack.manifeste.get('statut')})")
        print("couches :", " ← ".join(r.versions))
        print(f"paramètres fiscaux : {len(r.parametres)} · règles de comptes : {len(r.comptes)} · "
              f"feuilles SN : {len(r.sn)} · contrôles : {len(r.controles)} · gabarits : {sorted(r.gabarits)}")
        for el, avant, apres in r.surcharges[:20]:
            print(f"  surcharge {el} : {avant} → {apres}")
        return 0
    if a.commande == "generer-cle":
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
        ident = a.args[0]
        prive = Path.home() / ".facil" / "cles" / f"{ident}.pem"
        public = DEPOT / "facil_moteur" / "packs" / "cles" / f"{ident}.pub"
        if prive.exists():
            print(f"clé déjà présente : {prive}"); return 1
        cle = Ed25519PrivateKey.generate()
        prive.parent.mkdir(parents=True, exist_ok=True)
        prive.write_bytes(cle.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
        public.write_bytes(cle.public_key().public_bytes(serialization.Encoding.PEM, serialization.PublicFormat.SubjectPublicKeyInfo))
        print(f"clé privée : {prive} (hors dépôt) · clé publique : {public}")
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
