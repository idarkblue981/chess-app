# Chess vs Stockfish AI

O aplicație de șah desktop modernă, dezvoltată în Python cu **Pygame**. Proiectul oferă o experiență de joc fluidă, o interfață adaptivă pentru ecrane mari și integrare cu motorul de analiză **Stockfish**.



## Caracteristici principale
* **Interfață Dinamică:** Fereastră Fullscreen cu centrare automată a tablei în funcție de rezoluția monitorului.
* **Panouri Laterale:** * **Stânga:** Istoric complet al mutărilor în notație algebrică (SAN) cu suport pentru scroll (rotiță mouse).
    * **Dreapta:** Panou simetric rezervat pentru funcționalități viitoare (ex. Buton Undo).
* **Motor Stockfish:** Adversar AI integrat cu nivel de dificultate ajustabil (implicit ELO 1400).
* **Reguli Complete:** Suport pentru rocada, en passant și meniu grafic dedicat pentru promovarea pionilor.
* **Design UI:** Etichete pentru jucători ("You" vs "Stockfish"), evidențierea ultimei mutări și sugestii vizuale pentru mutări legale.

## Tehnologii utilizate
* **Python 3.x**
* **Pygame:** Randare grafică, gestionarea evenimentelor și sunet.
* **python-chess:** Logica jocului, validarea mutărilor și generarea notației SAN.
* **Stockfish Engine:** Motor extern pentru calculul mutărilor AI.