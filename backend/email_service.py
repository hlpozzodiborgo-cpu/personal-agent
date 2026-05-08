"""
Service pour envoyer les recommandations par email
Phase 2: Alertes email aux utilisateurs
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict
import os

logger = logging.getLogger(__name__)


class EmailService:
    """Service pour envoyer les emails de recommandations"""
    
    @staticmethod
    def send_recommendation_email(
        recipient_email: str,
        recommendations: List[Dict],
        portfolio_value: float = 0
    ) -> bool:
        """
        Envoie un email avec les recommandations du jour
        
        Args:
            recipient_email: Email de destination
            recommendations: Liste des recommandations
            portfolio_value: Valeur du portefeuille (optionnel)
            
        Returns:
            True si succès, False sinon
        """
        
        # Configuration SMTP (Gmail ou autre)
        # NOTE: Pour production, utiliser des variables d'environnement
        SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
        SENDER_EMAIL = os.getenv("SENDER_EMAIL")
        SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
        
        # Si pas de config, retourner False
        if not SENDER_EMAIL or not SENDER_PASSWORD:
            logger.warning("⚠️ Email non configuré - SMTP_SERVER/EMAIL/PASSWORD manquants")
            return False
        
        try:
            # Créer le message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = f"🚀 Investor AI - {len(recommendations)} recommandations"
            msg["From"] = SENDER_EMAIL
            msg["To"] = recipient_email
            
            # Générer le contenu HTML
            html_content = EmailService._generate_html_email(
                recommendations, portfolio_value
            )
            
            # Attacher le contenu
            msg.attach(MIMEText(html_content, "html"))
            
            # Envoyer via SMTP
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_PASSWORD)
                server.send_message(msg)
            
            logger.info(f"✅ Email envoyé à {recipient_email}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error("❌ Erreur SMTP: Identifiants invalides")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ Erreur SMTP: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Erreur envoi email: {e}")
            return False

    @staticmethod
    def _generate_html_email(recommendations: List[Dict], portfolio_value: float) -> str:
        """Génère le contenu HTML de l'email"""
        
        # Compter les types de recommandations
        buy_count = sum(1 for r in recommendations if "BUY" in r['recommendation_type'])
        sell_count = sum(1 for r in recommendations if "SELL" in r['recommendation_type'])
        hold_count = sum(1 for r in recommendations if "HOLD" in r['recommendation_type'])
        
        recommendations_html = ""
        
        # Grouper par type
        for rec_type in ["BUY 🟢", "SELL 🔴", "HOLD ⚪", "MONITOR 🟡"]:
            filtered = [r for r in recommendations if r['recommendation_type'] == rec_type]
            
            if filtered:
                recommendations_html += f"""
                <h3 style="color: #2c3e50; border-left: 4px solid #3498db; padding-left: 15px; margin-top: 20px;">
                    {rec_type}
                </h3>
                """
                
                for rec in filtered:
                    recommendations_html += f"""
                    <div style="background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 3px solid #3498db;">
                        <h4 style="margin: 0 0 5px 0; color: #2c3e50;">
                            <strong>{rec['symbol']}</strong> - {rec['sentiment_label']}
                        </h4>
                        <p style="margin: 5px 0; color: #555;">
                            <strong>Titre:</strong> {rec['title']}
                        </p>
                        <p style="margin: 5px 0; color: #555;">
                            <strong>Résumé:</strong> {rec['summary'][:150]}...
                        </p>
                        <p style="margin: 5px 0; color: #888; font-size: 12px;">
                            <strong>Source:</strong> {rec['source']} | 
                            <strong>Confiance:</strong> {rec['confidence']}% |
                            <strong>Sentiment:</strong> {rec['sentiment_score']}
                        </p>
                        <a href="{rec['url']}" style="color: #3498db; text-decoration: none;">
                            Lire l'article →
                        </a>
                    </div>
                    """
        
        # Template HTML
        html = f"""
        <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 28px; }}
                    .summary {{ background: #ecf0f1; padding: 15px; margin: 20px 0; border-radius: 5px; }}
                    .summary-item {{ display: inline-block; margin-right: 20px; }}
                    .summary-item strong {{ color: #2c3e50; }}
                    .footer {{ text-align: center; color: #888; font-size: 12px; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>💰 Investor AI</h1>
                        <p>Vos recommandations d'investissement du jour</p>
                    </div>
                    
                    <div class="summary">
                        <h3 style="margin-top: 0;">📊 Résumé du jour</h3>
                        <div class="summary-item">
                            <strong>🟢 À acheter:</strong> {buy_count}
                        </div>
                        <div class="summary-item">
                            <strong>🔴 À vendre:</strong> {sell_count}
                        </div>
                        <div class="summary-item">
                            <strong>⚪ À tenir:</strong> {hold_count}
                        </div>
                        {f'<div class="summary-item"><strong>💼 Portefeuille:</strong> ${portfolio_value:,.2f}</div>' if portfolio_value > 0 else ''}
                    </div>
                    
                    {recommendations_html}
                    
                    <div class="footer">
                        <p>
                            💡 <strong>Disclaimer:</strong> Ces recommandations sont générées automatiquement 
                            basées sur l'analyse du sentiment des actualités. Elles ne constituent pas des conseils 
                            financiers professionnels. Consultez un expert avant d'investir.
                        </p>
                        <p>
                            Investor AI - Votre analyste financier personnel
                        </p>
                    </div>
                </div>
            </body>
        </html>
        """
        
        return html

    @staticmethod
    def test_email_config(recipient_email: str) -> bool:
        """Teste la configuration email"""
        logger.info(f"📧 Test d'envoi d'email à {recipient_email}")
        
        test_recommendations = [
            {
                'symbol': 'TEST',
                'title': 'Test Email Configuration',
                'summary': 'Ceci est un email de test',
                'source': 'Investor AI',
                'url': 'https://localhost:3000',
                'sentiment_label': 'Neutre',
                'recommendation_type': 'HOLD ⚪',
                'confidence': 50,
                'sentiment_score': 0.0
            }
        ]
        
        return EmailService.send_recommendation_email(recipient_email, test_recommendations)
