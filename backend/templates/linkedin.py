"""
Templates de posts LinkedIn.
Structures réutilisables pour génération IA.
"""

from typing import Dict, Any


LINKEDIN_TEMPLATES: Dict[str, Any] = {
    "classic": {
        "name": "Post Classique",
        "description": "Format viral avec hook + développement + CTA",
        "structure": {
            "hook": {
                "max_words": 10,
                "style": "percutant, intrigant, ou provoquant"
            },
            "body": {
                "paragraphs": [3, 5],
                "paragraph_length": "court (2-3 lignes)",
                "style": "conversationnel, authentique"
            },
            "cta": {
                "type": "question ou invitation",
                "examples": [
                    "Et toi, tu as déjà vécu ça ?",
                    "Raconte-moi en commentaire.",
                    "Partage si tu es d'accord !"
                ]
            },
            "hashtags": {
                "count": [2, 5],
                "relevance": "pertinents au secteur"
            }
        },
        "example": """[Hook percutant]

[Paragraphe 1: Contexte ou problème]

[Paragraphe 2: Développement]

[Paragraphe 3: Solution ou insight]

[CTA clair]

#HashtagPertinent #Secteur"""
    },

    "storytelling": {
        "name": "Storytelling",
        "description": "Raconte une histoire personnelle avec leçon",
        "structure": {
            "hook": {
                "type": "début d'histoire",
                "style": "immersif, personnel"
            },
            "story": {
                "paragraphs": [4, 6],
                "arc": "situation → conflit → résolution",
                "tone": "authentique, vulnérable"
            },
            "lesson": {
                "type": "enseignement tiré de l'histoire",
                "style": "applicable, actionnable"
            },
            "cta": {
                "type": "invitation à partager son expérience"
            }
        },
        "example": """Il y a 3 ans, j'étais au fond du trou.

[Histoire personnelle en 4-5 paragraphes]

Ce que j'ai appris:
[Leçon applicable]

Et toi, tu as déjà vécu ça ?

#PersonalBranding #Entrepreneuriat"""
    },

    "list": {
        "name": "Liste/Tips",
        "description": "Liste de conseils numérotés",
        "structure": {
            "hook": {
                "type": "promesse de valeur",
                "format": "X choses que..., X erreurs..., X conseils..."
            },
            "items": {
                "count": [3, 7],
                "format": "1. [Titre] - [Explication courte]",
                "style": "actionnable, concret"
            },
            "conclusion": {
                "type": "récap + CTA"
            }
        },
        "example": """5 erreurs que font 90% des solopreneurs en personal branding:

1. [Erreur 1]
→ [Pourquoi c'est problématique]

2. [Erreur 2]
→ [Explication]

...

Tu en fais combien ?

#Solopreneur #PersonalBranding"""
    },

    "controversial": {
        "name": "Prise de Position",
        "description": "Opinion tranchée pour provoquer l'engagement",
        "structure": {
            "hook": {
                "type": "affirmation controversée",
                "style": "direct, assumé"
            },
            "argumentation": {
                "paragraphs": [3, 4],
                "style": "arguments solides mais provocants"
            },
            "nuance": {
                "optional": True,
                "type": "reconnaître le point de vue opposé"
            },
            "cta": {
                "type": "invitation au débat"
            }
        },
        "example": """Unpopular opinion:

[Affirmation controversée]

Pourquoi je pense ça:
[Arguments]

Tu es d'accord ou pas du tout ?

#PersonalBranding #HotTake"""
    },

    "behind_the_scenes": {
        "name": "Coulisses",
        "description": "Montre les coulisses de ton activité",
        "structure": {
            "hook": {
                "type": "invitation dans l'intimité",
                "examples": [
                    "Ce que personne ne voit...",
                    "La réalité derrière...",
                    "Aujourd'hui je vous montre..."
                ]
            },
            "reveal": {
                "type": "processus, échec, ou vérité cachée",
                "tone": "authentique, transparent"
            },
            "lesson": {
                "type": "ce que ça t'a appris"
            }
        },
        "example": """Ce matin, j'ai passé 3h sur un post LinkedIn.

Et je l'ai supprimé.

Pourquoi ?
[Explication des coulisses]

Ce que ça m'a appris:
[Leçon]

#Authenticité #Solopreneur"""
    }
}


def get_template_prompt(template_key: str, topic: str, tone: str) -> str:
    """
    Génère un prompt pour l'IA basé sur un template.
    """
    template = LINKEDIN_TEMPLATES.get(template_key, LINKEDIN_TEMPLATES["classic"])

    prompt = f"""Génère un post LinkedIn en utilisant le template "{template['name']}".

SUJET: {topic}
TON: {tone}

STRUCTURE:
{template['structure']}

EXEMPLE DE FORMAT:
{template['example']}

Retourne UNIQUEMENT le post, sans méta-commentaires.
"""

    return prompt
