# Stratégie IA — gratuit vs payant
### Note de cadrage (à présenter au client)

## Le principe : un produit, un levier

On ne livre pas « du gratuit » ni « du payant ». On livre **un seul produit**
avec un **levier** : une variable (`MODEL_PROVIDER`) qui fait basculer le moteur
d'IA sans toucher au reste du code. Le client choisit son curseur
**coût / performance** ; nous, on garantit que ça marche dans les deux cas.

C'est rendu possible par l'architecture **swappable** : le modèle est isolé
derrière une interface. Le remplacer ne change pas l'API, ni l'interface, ni le
pipeline. Une ligne, et on passe du mock au modèle local, ou à Claude.

## Gratuit vs payant : ce que ça change vraiment

Tout, sauf le modèle, est **gratuit et le reste** : le code et les frameworks
(Python, FastAPI, Gradio, Docker), le dépôt GitHub, et l'hébergement de démo
(Hugging Face Spaces, lien Gradio, tunnel). Le **seul vrai poste de coût, c'est
le modèle d'IA** — et c'est précisément là que se joue l'arbitrage.

| Niveau | Coût | Pour quoi |
|---|---|---|
| Mock (heuristique) | Gratuit | Démontrer le pipeline, pas de la vraie IA |
| Modèle open-source local (Ollama, HF) | Gratuit | Confidentiel, mais lourd, plus lent, qualité moindre |
| API gratuites (Groq, Gemini free, OpenRouter) | Gratuit* | Démo / faible volume — *voir contreparties |
| API payantes (Anthropic, OpenAI) | Quelques centimes | Production : qualité, débit, confidentialité |

## Les contreparties du gratuit — à dire au client À CHAQUE FOIS

Le gratuit n'est jamais sans contrepartie. C'est notre devoir de transparence :

- **Données** : la plupart des offres gratuites peuvent réutiliser ce que tu
  envoies pour entraîner leurs modèles. Pour une entreprise, c'est une fuite de
  données confidentielles. Les API **payantes n'entraînent pas** sur tes données.
- **Limites de débit** : quelques dizaines de requêtes/minute. Tient pour une
  démo, pas pour traiter des milliers de fichiers.
- **Fiabilité** : un service gratuit peut être lent, saturé, ou supprimé du jour
  au lendemain. Aucun engagement.
- **Qualité** : sur des demandes précises, un modèle payant haut de gamme est
  nettement plus fin et constant.

> En clair : « quand c'est gratuit, c'est qu'on attend une contrepartie ». Le
> client doit le comprendre pour décider en connaissance de cause.

## Notre méthode

Briefer, partir d'un truc **cliquable** (une démo qui tourne), puis **réduire à
l'essentiel le plus efficace**. On ne sur-construit pas : on montre que ça marche,
on simplifie, et on laisse au client le levier coût/performance.

## Ce qu'on facture

Pas le modèle (le client le paie au réel s'il choisit le payant). On facture la
**prestation** : l'architecture, l'intégration, le conseil, et le fait d'avoir
posé le choix au lieu de le subir. C'est ça, la valeur.
