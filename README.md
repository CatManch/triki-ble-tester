# Triki BLE Controller 🎮
![Triki](https://img.shields.io/badge/Token-Auto%20Updated-brightgreen)
## Spis treści
1. [Opis projektu](#opis-projektu)
2. [Funkcjonalności](#funkcjonalności)
3. [Architektura techniczna](#architektura-techniczna)
4. [Wymagania systemowe](#wymagania-systemowe)
5. [Instalacja](#instalacja)
6. [Instrukcja obsługi](#instrukcja-obsługi)
7. [Rozwiązywanie problemów](#rozwiązywanie-problemów)
8. [Licencja](#licencja)

---

## Opis projektu

**Triki BLE Controller** to projekt typu "IoT Desktop Integration", który pozwala na zamianę fizycznego urządzenia z sensorem IMU w bezprzewodowy kontroler ruchu dla komputera. Dzięki wykorzystaniu protokołu **Bluetooth Low Energy (BLE)** oraz biblioteki **Bleak**, program odczytuje dane akcelerometru w czasie rzeczywistym i mapuje je na ruch obiektu w środowisku 2D (Pygame).

## Funkcjonalności

* **Dynamiczne sterowanie 2D:** Płynne przesuwanie kwadratu na ekranie bazujące na nachyleniu urządzenia.
* **Rotacja w czasie rzeczywistym:** Wykorzystanie osi Z do obracania obiektu (orientacja kierunkowa).
* **System autokalibracji:** Możliwość "wyzerowania" czujnika w dowolnej pozycji, co eliminuje problem dryfu (driftu) sensorów MEMS.
* **Synchronizacja strumienia danych:** Mechanizm czyszczenia bufora BLE, zapewniający stabilne odczyty bez opóźnień (lagów).
* **Konfigurowalne parametry:** Łatwa modyfikacja czułości, martwej strefy (deadzone) oraz prędkości maksymalnej wewnątrz kodu.

## Architektura techniczna

Projekt opiera się na pętli zdarzeń `asyncio`, co pozwala na jednoczesną komunikację Bluetooth oraz renderowanie grafiki bez blokowania interfejsu użytkownika.

Dane przesyłane są w paczkach 10-bajtowych. Parser wykorzystuje strukturę `struct.unpack("<hhhhh", ...)` do dekodowania danych w formacie *Little Endian*, zapewniając kompatybilność z mikrokontrolerami.

## Wymagania systemowe

* **System operacyjny:** Windows 10/11.
* **Hardware:** Komputer z obsługą Bluetooth 4.0+, urządzenie "Triki".
* **Oprogramowanie:** Python 3.13+.

## Instalacja

1. Sklonuj repozytorium:

```bash
git clone https://github.com/twoja-nazwa/triki-ble-controller.git
cd triki-ble-controller
```

2. Zainstaluj wymagane zależności:

```bash
pip install pygame bleak
```

## Instrukcja obsługi

1. **Uruchomienie:**  
Uruchom skrypt w terminalu:

```bash
python Triki5.py
```

2. **Synchronizacja:**  
Po nawiązaniu połączenia, połóż urządzenie na płaskiej powierzchni.

3. **Kalibracja:**  
Naciśnij klawisz **K**. Program zbierze próbki tła i ustawi środek.

4. **Sterowanie:**

* Przechylenie (przód/tył/lewo/prawo) → ruch kwadratu.
* Obrót w osi Z → rotacja kwadratu.
* Klawisz **K** → reset pozycji i rekalibracja.

## Rozwiązywanie problemów

* **Urządzenie nie reaguje:**  
Upewnij się, że urządzenie jest naładowane i znajduje się w zasięgu Bluetooth.

* **Kwadrat ucieka (Dryf):**  
Jest to normalne zachowanie czujników MEMS. Połóż urządzenie płasko i naciśnij ponownie **K**.

* **Błąd połączenia:**  
W przypadku problemów z debuggerem VS Code, preferuj uruchomienie komendą:

```bash
python Triki5.py
```

## Licencja

Projekt jest udostępniony na licencji MIT. Możesz dowolnie modyfikować i rozwijać kod.

*Stworzono z pasją do robotyki i programowania.*