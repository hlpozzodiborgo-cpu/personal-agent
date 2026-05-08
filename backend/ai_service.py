"""
Service d'analyse IA via Claude (Anthropic).

Fonctionnement :
- Appelé à la demande (pas en arrière-plan en permanence)
- Reçoit des articles de presse + le contexte du portefeuille
- Envoie un prompt structuré à Claude Haiku (modèle rapide et économique)
- Claude retourne une analyse JSON : signal, impact, explication en français
- Coût typique : ~0.001 € pour 10 articles (moins d'un centime)
"""
import json
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

_anthropic_key_override: Optional[str] = None


class AIService:

    @staticmethod
    def get_api_key() -> Optional[str]:
        global _anthropic_key_override
        if _anthropic_key_override:
            return _anthropic_key_override
        from config import ANTHROPIC_API_KEY
        return ANTHROPIC_API_KEY

    @staticmethod
    def set_api_key(key: str) -> None:
        global _anthropic_key_override
        _anthropic_key_override = key or None

    @staticmethod
    def analyze_news_for_portfolio(
        articles: List[Dict],
        holdings: List[Dict],
    ) -> Dict:
        """
        Analyse des articles de presse avec Claude.

        holdings : liste de dicts avec symbol, name, quantity,
                   avg_price, current_price, gain_pct
        articles  : liste de dicts avec title, description, source, date, url

        Retourne un dict avec :
          - market_summary : résumé global du marché en français
          - articles       : analyse par article (signal, impact, confiance, etc.)
          - error          : message d'erreur si la clé manque ou si l'appel échoue
        """
        api_key = AIService.get_api_key()
        if not api_key:
            return {
                "error": "Clé Anthropic non configurée — ajoutez-la dans Paramètres.",
                "articles": [],
                "market_summary": "",
            }

        if not articles:
            return {"articles": [], "market_summary": "Aucune actualité à analyser."}

        # Contexte portefeuille
        portfolio_lines = []
        for h in holdings:
            sign = "+" if h.get("gain_pct", 0) >= 0 else ""
            portfolio_lines.append(
                f"  - {h['symbol']} ({h['name']}) : {h['quantity']} parts, "
                f"PRU {h['avg_price']:.2f}€, cours actuel {h['current_price']:.2f}€ "
                f"({sign}{h.get('gain_pct', 0):.1f}%)"
            )
        portfolio_text = "\n".join(portfolio_lines) if portfolio_lines else "  Portefeuille vide"

        # Articles (15 max pour limiter les tokens)
        capped = articles[:15]
        articles_text = "\n\n".join(
            f"[{i + 1}] \"{a['title']}\" — {a.get('source', '?')}, {a.get('date', '?')}\n"
            f"{a.get('description', '(pas de description)')[:300]}"
            for i, a in enumerate(capped)
        )

        prompt = f"""Tu es un analyste financier personnel. Analyse ces actualités pour le portefeuille suivant.

PORTEFEUILLE :
{portfolio_text}

ACTUALITÉS RÉCENTES :
{articles_text}

Instructions :
- Pour chaque article numéroté, évalue sa pertinence pour CE portefeuille précis.
- Donne un signal clair et une explication courte en français (2-3 phrases maximum).
- Tiens compte des ETF indiciels (ESE.PA suit le S&P 500, WPEA.PA suit le MSCI World, etc.).
- Sois concis et direct.

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

        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}],
            )

            raw = response.content[0].text.strip()
            # Extraire le JSON si emballé dans un bloc markdown
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()

            result = json.loads(raw)
            result["model"] = "claude-haiku-4-5-20251001"
            result["articles_count"] = len(capped)
            return result

        except json.JSONDecodeError as e:
            logger.error(f"Claude JSON parse error: {e}")
            return {"error": "Réponse IA non parseable.", "articles": [], "market_summary": ""}
        except Exception as e:
            logger.error(f"Claude API error: {e}")
            return {"error": str(e), "articles": [], "market_summary": ""}
