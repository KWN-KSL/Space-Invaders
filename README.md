# Space Invaders

Klasyczna gra zręcznościowa stworzona w Pythonie z użyciem biblioteki Pygame, z dodatkowymi elementami jak bossowie, asteroidy, animacje i system zapisu stanu gry.

## 🎮 Opis gry

W grze **Space Invaders** sterujesz statkiem kosmicznym, który porusza się po dolnej części ekranu i eliminuje fale nadlatujących przeciwników. Z każdym poziomem trudności przeciwnicy stają się szybszi i bardziej agresywni.

Twoim celem jest przetrwanie i zdobycie jak największej liczby punktów. W ostatniej fali pojawia się **Boss — Mothership**, który wymaga wielu trafień i wypuszcza śmiercionośne asteroidy.

---

## 🧠 Twórca projektu

Kewin Kisiel — 197866  

---

## 🛠️ Technologie

- **Język:** Python 3  
- **Biblioteki:** Pygame  
- **IDE:** Visual Studio Code

---

## 🕹️ Sterowanie

| Klawisz | Działanie                        |
|--------|-----------------------------------|
| ← / → lub A / D | Ruch gracza              |
| Spacja / LPM / PPM | Strzał                |
| ESC    | Pauza                             |
| Mysz   | Nawigacja po menu                 |
| 1–6    | Skróty w menu pauzy               |

---

## 🧭 Menu główne

![Menu](Menu.png)

## 📦 Tryby gry i funkcje

![Wybór trudności](wybor_trudnosci.png)

## 🎯 Poziomy trudności
W grze dostępne są trzy poziomy trudności, które wpływają na życie gracza, prędkość i agresywność przeciwników oraz wytrzymałość bossa i asteroid:
### 🟢 Łatwy
-3 życia
- Najwolniejsi i najmniej agresywni przeciwnicy
- Boss: 20 HP
- Asteroidy: 2 HP
### 🟡 Średni
- 2 życia
- Szybsi i częściej strzelający przeciwnicy
- Boss: 30 HP
- Asteroidy: 3 HP
### 🔴 Trudny
- 1 życie
- Najszybsi i bardzo agresywni przeciwnicy
- Boss: 50 HP
- Asteroidy: 5 HP
### 👾 Boss (Tryb Bossa)
- 1 życie
- Rozgrywka polega wyłącznie na walce z bossem (Mothership)
- Przeciwnicy nie pojawiają się — tylko boss i asteroidy
- Boss: 50 HP
- Asteroidy: 5 HP

## 🌊 Fale przeciwników
- **Fala 1–2:** klasyczni przeciwnicy  
- **Fala 3:** Boss (Mothership) + asteroidy

## 👾 Boss i asteroidy

![Starcie z bossem](boss.png)

- Boss ma pasek życia, potrafi strzelać i wypuszcza asteroidy.  
- Gracz może niszczyć zarówno bossa, jak i asteroidy.

## 💾 System zapisu gry
- Autozapis co sekundę  
- Możliwość cofnięcia się o 5 zapisów (kosztem 5 punktów)

## 💥 Efekty
- Animacje eksplozji i respawnu  
- Różne ścieżki dźwiękowe w zależności od stanu gry

---

## 📸 Rozgrywka

![Rozgrywka](gra.png)

---

## 📥 Pobieranie

Jeśli chcesz zagrać bez instalowania Pythona:

👉 **[Kliknij tutaj, aby pobrać wersję .zip z grą (.exe)](link_do_zipa)**  
(Wymagany system Windows, brak potrzeby instalacji)


---

## 🚀 Uruchamianie z kodu źródłowego
1. Zainstaluj bibliotekę pygame:
   pip install pygame
   
## 🧾 Licencja
Projekt edukacyjny — brak komercyjnej licencji. Wykorzystywany w celach naukowych.

## 🙌 Podziękowania
Specjalne podziękowania dla testerów:
- 👤 1glotta
- 👤 Gmblr
- 👤 BillyChappo
