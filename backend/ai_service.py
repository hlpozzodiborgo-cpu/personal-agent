"""
Service d'analyse IA multi-fournisseur.

Fournisseurs supportés :
  - claude  : Anthropic Claude Haiku (~0.001 $/analyse, $5 crédits offerts)
  - gemini  : Google Gemini 1.5 Flash (GRATUIT — 1 M tokens/jour, 15 req/min)
  - groq    : Groq avec Llama 3.1 70B  (GRATUIT — 14 400 req/jour)

Le fournisseur actif est configurable dans Paramètres.
L'analyse est déclenchée à la demande (pas en arrière-plan).
"""
import json
import logging
import requests
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_anthropic_key: Optional[str] = None
_gemini_key:    Optional[str] = None
_groq_key:      Optional[str] = None
_provider:      str = "claude"   # valeur par défaut


class AIService:

    # ── Gestion des clés et du fournisseur ──────────────────────────────────

    @staticmethod
    def get_api_key() -> Optional[str]:
        global _anthropic_key
        if _anthropic_key:
            return _anthropic_key
        from config import ANTHROPIC_API_KEY
        return ANTHROPIC_API_KEY

    @staticmethod
    def set_api_key(key: str) -> None:
        global _anthropic_key
        _anthropic_key = key or None

    @staticmethod
    def get_gemini_key() -> Optional[str]:
        return _gemini_key

    @staticmethod
    def set_gemini_key(key: str) -> None:
        global _gemini_key
        _gemini_key = key or None

    @staticmethod
    def get_groq_key() -> Optional[str]:
        return _groq_key

    @staticmethod
    def set_groq_key(key: str) -> None:
        global _groq_key
        _groq_key = key or None

    @staticmethod
    def get_provider() -> str:
        return _provider

    @staticmethod
    def set_provider(provider: str) -> None:
        global _provider
        if provider in ("claude", "gemini", "groq"):
            _provider = provider

    # ── Tests de connexion ──────────────────────────────────────────────────

    @staticmethod
    def test_gemini() -> Dict:
        key = AIService.get_gemini_key()
        if not key:
            return {"success": False, "message": "Cle non configuree"}
        try:
            r = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                params={"key": key},
                json={"contents": [{"parts": [{"text": "Reply: OK"}]}]},
                timeout=8,
            )
            if r.status_code == 200:
                return {"success": True, "message": "Gemini 1.5 Flash connecte — FREE tier actif"}
            if r.status_code == 400:
                return {"success": False, "message": "Cle invalide (API key not valid)"}
            return {"success": False, "message": f"Erreur HTTP {r.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)[:120]}

    @staticmethod
    def test_groq() -> Dict:
        key = AIService.get_groq_key()
        if not key:
            return {"success": False, "message": "Cle non configuree"}
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-8b-instant", "messages": [{"role": "user", "content": "Reply: OK"}], "max_tokens": 4},
                timeout=8,
            )
            if r.status_code == 200:
                model = r.json().get("model", "groq")
                return {"success": True, "message": f"Groq connecte — modele {model} — FREE tier actif"}
            if r.status_code == 401:
                return {"success": False, "message": "Cle invalide"}
            return {"success": False, "message": f"Erreur HTTP {r.status_code}"}
        except Exception as e:
            return {"success": False, "message": str(e)[:120]}

    # ── Analyse principale ──────────────────────────────────────────────────

    @staticmethod
    def analyze_news_for_portfolio(articles: List[Dict], holdings: List[Dict]) -> Dict:
        """
        Dispatch vers le bon fournisseur selon le réglage actif.
        """
        provider = AIService.get_provider()
        if provider == "gemini":
            return AIService._analyze_gemini(articles, holdings)
        if provider == "groq":
            return AIService._analyze_groq(articles, holdings)
        return AIService._analyze_claude(articles, holdings)

    # ── Prompt partagé ──────────────────────────────────────────────────────

    @staticmethod
    def _build_prompt(articles: List[Dict], holdings: List[Dict]) -> str:
        portfolio_lines = []
        for h in holdings:
            sign = "+" if h.get("gain_pct", 0) >= 0 else ""
            portfolio_lines.append(
                f"  - {h['symbol']} ({h['name']}) : {h['quantity']} parts, "
                f"PRU {h['avg_price']:.2f}€, cours {h['current_price']:.2f}€ "
                f"({sign}{h.get('gain_pct', 0):.1f}%)"
            )
        portfolio_text = "\n".join(portfolio_lines) if portfolio_lines else "  Portefeuille vide"

        capped = articles[:15]
        articles_text = "\n\n".join(
            f"[{i+1}] \"{a['title']}\" — {a.get('source','?')}, {a.get('date','?')}\n"
            f"{a.get('description','')[:300]}"
            for i, a in enumerate(capped)
        )

        return f"""Tu es un analyste financier personnel. Analyse ces actualités pour le portefeuille suivant.

PORTEFEUILLE :
{portfolio_text}

ACTUALITÉS RÉCENTES :
{articles_text}

Instructions :
- Pour chaque article numéroté, évalue sa pertinence pour CE portefeuille précis.
- Tiens compte des ETF indiciels (ESE.PA suit le S&P 500, WPEA.PA le MSCI World, etc.).
- Donne un signal clair et une explication courte en français (2-3 phrases).

Réponds UNIQUEMENT avec ce JSON valide (aucun texte avant ou après) :
{{
  "market_summary": "2-3 phrases résumant le sentiment général du marché en français",
  "articles": [
    {{
      "index": 1,
      "relevance": "haute|moyenne|faible",
      "impact": "positif|negatif|neutre",
      "signal": "RENFORCER|ALLEGER|SURVEILLER|CONSERVER|AUCUN",
      "affected_symbols": ["SYMBOL"],
      "analysis": "Explication courte en français adaptée au portefeuille.",
      "confidence": 70
    }}
  ]
}}"""

    @staticmethod
    def _parse_json_response(raw: str) -> Dict:
        raw = raw.strip()
        if "```json" in raw:
            raw = raw.split("```json")[1].split("```")[0].strip()
        elif "```" in raw:
            raw = raw.split("```")[1].split("```")[0].strip()
        return json.loads(raw)

    # ── Implémentations par fournisseur ─────────────────────────────────────

    @staticmethod
    def _analyze_claude(articles: List[Dict], holdings: List[Dict]) -> Dict:
        api_key = AIService.get_api_key()
        if not api_key:
            return {"error": "Clé Anthropic non configurée — ajoutez-la dans Paramètres.", "articles": [], "market_summary": ""}
        if not articles:
            return {"articles": [], "market_summary": "Aucune actualité à analyser."}
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-haiku-4-5-20251001", max_tokens=2048,
                messages=[{"role": "user", "content": AIService._build_prompt(articles, holdings)}],
            )
            result = AIService._parse_json_response(response.content[0].text)
            result["model"] = "Claude Haiku"
            result["articles_count"] = len(articles[:15])
            return result
        except json.JSONDecodeError:
            return {"error": "Réponse IA non parseable.", "articles": [], "market_summary": ""}
        except Exception as e:
            logger.error(f"Claude error: {e}")
            return {"error": str(e), "articles": [], "market_summary": ""}

    @staticmethod
    def _analyze_gemini(articles: List[Dict], holdings: List[Dict]) -> Dict:
        api_key = AIService.get_gemini_key()
        if not api_key:
            return {"error": "Clé Gemini non configurée — ajoutez-la dans Paramètres.", "articles": [], "market_summary": ""}
        if not articles:
            return {"articles": [], "market_summary": "Aucune actualité à analyser."}
        try:
            r = requests.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
                params={"key": api_key},
                json={"contents": [{"parts": [{"text": AIService._build_prompt(articles, holdings)}]}],
                      "generationConfig": {"temperature": 0.2, "maxOutputTokens": 2048}},
                timeout=30,
            )
            if r.status_code != 200:
                return {"error": f"Gemini erreur {r.status_code}: {r.text[:120]}", "articles": [], "market_summary": ""}
            raw = r.json()["candidates"][0]["content"]["parts"][0]["text"]
            result = AIService._parse_json_response(raw)
            result["model"] = "Gemini 1.5 Flash (gratuit)"
            result["articles_count"] = len(articles[:15])
            return result
        except json.JSONDecodeError:
            return {"error": "Réponse Gemini non parseable.", "articles": [], "market_summary": ""}
        except Exception as e:
            logger.error(f"Gemini error: {e}")
            return {"error": str(e), "articles": [], "market_summary": ""}

    @staticmethod
    def _analyze_groq(articles: List[Dict], holdings: List[Dict]) -> Dict:
        api_key = AIService.get_groq_key()
        if not api_key:
            return {"error": "Clé Groq non configurée — ajoutez-la dans Paramètres.", "articles": [], "market_summary": ""}
        if not articles:
            return {"articles": [], "market_summary": "Aucune actualité à analyser."}
        try:
            r = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": "llama-3.1-70b-versatile",
                      "messages": [{"role": "user", "content": AIService._build_prompt(articles, holdings)}],
                      "max_tokens": 2048, "temperature": 0.2},
                timeout=30,
            )
            if r.status_code != 200:
                return {"error": f"Groq erreur {r.status_code}", "articles": [], "market_summary": ""}
            raw = r.json()["choices"][0]["message"]["content"]
            result = AIService._parse_json_response(raw)
            result["model"] = "Llama 3.1 70B via Groq (gratuit)"
            result["articles_count"] = len(articles[:15])
            return result
        except json.JSONDecodeError:
            return {"error": "Réponse Groq non parseable.", "articles": [], "market_summary": ""}
        except Exception as e:
            logger.error(f"Groq error: {e}")
            return {"error": str(e), "articles": [], "market_summary": ""}
