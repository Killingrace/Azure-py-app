# Dokumentacja Systemu Informatycznego „Liga”
**Autorzy:** Anton Leskovets, Dmytro Shutko  
**Technologie:** React (Frontend), FastAPI (Backend), PostgreSQL (Baza Danych), Azure (Chmura)

---

## 1. Logiczny podział aplikacji na trzy główne komponenty

Architektura systemu „Liga” została zaprojektowana w klasycznym, trójwarstwowym modelu, który zapewnia pełną separację odpowiedzialności (Separation of Concerns). Pozwala to na niezależny rozwój, testowanie oraz skalowanie każdego z komponentów.

```
       +---------------------------------------------+
       |           Frontend (React SPA)              |
       |  Prezentacja danych, GUI, obsługa sesji     |
       +---------------------------------------------+
                              ^
                              | HTTPS / JSON (REST API)
                              v
       +---------------------------------------------+
       |          Backend (FastAPI Engine)           |
       |  Autoryzacja JWT, reguły biznesowe, CRUD    |
       +---------------------------------------------+
                              ^
                              | Asynchroniczne zapytania SQL
                              v
       +---------------------------------------------+
       |          Baza Danych (PostgreSQL)           |
       |  Trwałość danych, relacje, spójność         |
       +---------------------------------------------+
```

### A. Frontend (Warstwa Prezentacji)
*   **Technologia:** React, TypeScript, Vite.
*   **Odpowiedzialność:**
    *   Prezentacja danych analitycznych (tabele wyników, klasyfikacja strzelców, sekcja analizy rywala - *Nemesis Analysis*).
    *   Interfejs administratora oraz trenera do zarządzania zasobami (ligami, drużynami, zawodnikami, terminarzem, meczami, wynikami i golami).
    *   Zarządzanie stanem aplikacji (Context API) w zakresie uwierzytelniania (`AuthContext`).
    *   Walidacja formularzy po stronie klienta oraz zapewnienie płynności interakcji (Single Page Application - SPA).

### B. Backend (Warstwa Logiki Biznesowej)
*   **Technologia:** Python, FastAPI, Pydantic, SQLAlchemy Async.
*   **Odpowiedzialność:**
    *   Udostępnianie bezpiecznego, bezstanowego interfejsu REST API pod ścieżką `/api/`.
    *   Implementacja mechanizmu uwierzytelniania i autoryzacji opartego o tokeny JWT (`auth.py`).
    *   Egzekwowanie reguł biznesowych (np. maksymalny limit 25 zawodników w drużynie, wymagana minimalna liczba 11 zawodników do utworzenia meczu).
    *   Przetwarzanie danych statystycznych i analitycznych na potrzeby Dashboardu.

### C. Warstwa Danych (Warstwa Trwałości)
*   **Technologia:** PostgreSQL, SQLAlchemy ORM (obiekty mapujące bazy danych).
*   **Odpowiedzialność:**
    *   Trwałe przechowywanie danych strukturalnych zgodnie z modelem relacyjnym (tabele: `leagues`, `schedules`, `teams`, `players`, `locations`, `games`, `scores`, `goals`, `users`).
    *   Zapewnienie integralności referencyjnej danych przy użyciu kluczy obcych (`ForeignKey`), indeksów unikalnych (`unique=True`) oraz kaskadowego usuwania powiązanych obiektów (`cascade="all, delete-orphan"`).
    *   Wydajne wykonywanie operacji agregacji i filtrowania na poziomie serwera bazy danych.

---

## 2. Kanały i protokoły komunikacji między komponentami

Płynna wymiana informacji pomiędzy komponentami została zoptymalizowana pod kątem wydajności i bezpieczeństwa:

1.  **Komunikacja Frontend <-> Backend:**
    *   **Protokół:** HTTPS. Wszystkie zapytania są szyfrowane, co chroni poufność przesyłanych danych (w tym haseł użytkowników oraz tokenów JWT).
    *   **Format danych:** JSON. Dane wejściowe wysyłane do API oraz odpowiedzi serwera są serializowane do formatu JSON.
    *   **Asynchroniczność:** Zapytania HTTP po stronie Reacta są realizowane asynchronicznie za pomocą klienta Axios (opakowanego w `ApiService` w pliku `api.ts`), co zapobiega blokowaniu interfejsu użytkownika podczas oczekiwania na odpowiedź serwera.

2.  **Komunikacja Backend <-> Baza Danych:**
    *   **Protokół/Mechanizm:** Połączenie TCP/IP realizowane za pośrednictwem asynchronicznego sterownika PostgreSQL (`psycopg_async`) zintegrowanego z SQLAlchemy.
    *   **Pula połączeń (Connection Pooling):** Silnik SQLAlchemy (`create_async_engine`) zarządza pulą połączeń do bazy danych PostgreSQL. Zapobiega to kosztownemu narzutowi czasowemu związanemu z nawiązywaniem nowego połączenia TCP przy każdym zapytaniu HTTP.
    *   **Sesje asynchroniczne (`AsyncSession`):** Każde zapytanie obsługiwane przez FastAPI pobiera z puli dedykowaną, asynchroniczną sesję (`get_db`), która jest zamykana natychmiast po zakończeniu transakcji, co zapobiega wyciekom zasobów.

---

## 3. Przepływy w kodzie oraz odpowiedzialność obiektów i metod

Projekt systemu cechuje ścisły podział na warstwy o różnym stopniu abstrakcji. Poniżej przedstawiono odpowiedzialności kluczowych modułów i przykładowy przepływ dla analizy rywala (*Nemesis*).

### Odpowiedzialność obiektów i modułów:
*   **`models.py` (Obiekty domenowe):** Definiują strukturę tabel bazy danych PostgreSQL za pomocą klas Pythonowych (SQLAlchemy). Każda klasa odpowiada jednej encji (np. klasa `Goal` powiązana z `Player`, `Team` i `Game`).
*   **`schemas.py` (Walidacja i Serializacja - Pydantic):**
    *   Definiują schematy danych wejściowych (np. `PlayerCreate`, `ScoreCreate`) oraz wyjściowych (np. `UserResponse`).
    *   Pydantic automatycznie weryfikuje typy danych (np. czy przesłany parametr `minute` to liczba całkowita) i odrzuca niepoprawne żądania kodem `422 Unprocessable Entity` zanim logika biznesowa podejmie jakiekolwiek działania.
*   **`auth.py` (Uwierzytelnianie i Bezpieczeństwo):**
    *   Metody `get_password_hash` i `verify_password` wykorzystują bibliotekę `bcrypt` do kryptograficznego zabezpieczania haseł.
    *   Metoda `create_access_token` generuje tokeny JWT.
    *   Metoda `get_current_user` (używana jako zależność FastAPI `Depends`) deszyfruje i weryfikuje token, pobierając aktualnego użytkownika z bazy, a `get_current_admin` dodatkowo weryfikuje rolę administratora.
*   **`crud.py` (Logika danych i zapytania):** Zawiera czyste zapytania SQLAlchemy. Metody te nie wiedzą o protokole HTTP ani o strukturze GUI – przyjmują jako parametr asynchroniczną sesję bazy danych `AsyncSession` oraz dane ze schematów Pydantic i zwracają obiekty bazodanowe.
*   **`main.py` (Kontrolery i API):** Wiąże wszystkie warstwy. Obsługuje routing HTTP, wywołuje zależności autoryzacyjne, przekazuje zapytania do metod w `crud.py` i zwraca dane zgodne ze schematami wyjściowymi.

### Przykład przepływu w kodzie: Wyznaczenie najlepszego zawodnika przeciwko danej drużynie (*Nemesis*)

Gdy użytkownik wybiera na Dashboardzie drużynę i klika przycisk „Analyze”, zachodzi następujący przepływ danych:

```
[GUI: Dashboard] --(HTTP GET /api/stats/best-player-vs-team/{team_id})--> [FastAPI: main.py]
                                                                                |
                                                                        (Zależność get_db)
                                                                                |
                                                                                v
[Baza danych] <--(SQL: JOIN, Group By, Count)-- [crud.py: get_best_player_vs_team]
      |
(Zwraca wiersz)
      |
      v
[crud.py: pobiera obiekt Player] --> [FastAPI: formatuje JSON] --(HTTP 200 JSON)--> [React GUI]
```

1.  **Warstwa prezentacji (React):** Komponent `Dashboard.tsx` wywołuje metodę `ApiService.getBestPlayerVsTeam(teamId)`.
2.  **Warstwa kontrolera (FastAPI):** Request trafia do endpointu w `main.py` pod ścieżkę `/api/stats/best-player-vs-team/{team_id}`.
3.  **Warstwa logiki danych (`crud.py`):** Wywoływana jest funkcja asynchroniczna `get_best_player_vs_team(db, team_id)`:
    ```python
    # Tworzenie podzapytania w celu pobrania ID meczów, w których grała dana drużyna (jako gospodarz lub gość)
    subq = select(models.Game.id).filter(
        or_(models.Game.home_team_id == team_id, models.Game.visitor_team_id == team_id)
    ).scalar_subquery()

    # Zliczanie goli dla poszczególnych zawodników strzelonych w tych meczach,
    # wykluczając gole strzelone przez zawodników analizowanej drużyny (team_id)
    stmt = select(
        models.Goal.player_id,
        func.count(models.Goal.id).label('goal_count')
    ).filter(
        models.Goal.game_id.in_(subq),
        models.Goal.team_id != team_id
    ).group_by(models.Goal.player_id).order_by(desc('goal_count'))

    # Wykonanie asynchronicznego zapytania SQL
    result = await db.execute(stmt)
    row = result.first()
    ```
4.  **Baza danych:** PostgreSQL wykonuje wydajne złączenia i agregacje na serwerze i zwraca jedynie rekord najbardziej niebezpiecznego gracza.
5.  **Warstwa kontrolera:** FastAPI serializuje wynik do JSONa i odsyła go do klienta.
6.  **Warstwa prezentacji:** Dashboard Reacta aktualizuje stan komponentu i wyświetla czerwony panel ostrzegawczy z nazwiskiem zawodnika i liczbą goli.

---

## 4. Wpływ komunikacji i przepływów na koszty i bezpieczeństwo

### Wpływ na koszty (Optymalizacja zasobów)
W chmurze publicznej (np. Microsoft Azure), koszty są bezpośrednio powiązane z czasem użycia procesora (CPU), pamięci RAM oraz wolumenem transferu danych. Zastosowane rozwiązania redukują te koszty:
*   **Minimalizacja transferu sieciowego (Network Payload):**
    *   Wszystkie odpowiedzi z bazy i API są ściśle filtrowane. W `schemas.py` zdefiniowano model `UserResponse`, który celowo pomija pole `hashed_password`. Ogranicza to rozmiar wysyłanych pakietów JSON.
    *   Stosowanie parametrów `skip` i `limit` (paginacja) w zapytaniach pobierających listy (np. graczy lub meczów) zapobiega jednorazowemu przesyłaniu tysięcy rekordów przez sieć.
*   **Optymalizacja kosztów obliczeniowych (Compute Costs):**
    *   Dzięki użyciu asynchronicznego frameworka FastAPI oraz sterownika PostgreSQL `psycopg_async`, serwer backendowy nie blokuje wątków podczas oczekiwania na bazę danych. Pojedynczy, tani kontener (np. Azure Container Apps w najtańszym planie zużycia za ok. 40-80 PLN/miesięcznie) potrafi obsłużyć setki jednoczesnych połączeń bez potrzeby autoskalowania w górę.
    *   Przeniesienie ciężaru obliczeń analitycznych na silnik bazy danych (np. agregowanie goli przy pomocy instrukcji `group_by` i `count` bezpośrednio w SQL, zamiast pobierania całej tabeli `goals` do pamięci RAM aplikacji Python) zapobiega wyciekom pamięci i pozwala na wykorzystanie tańszego serwera aplikacyjnego.

### Wpływ na bezpieczeństwo
Architektura komunikacji eliminuje popularne podatności sieciowe:
*   **Brak sesji po stronie serwera (Stateless Architecture):** Backend nie przechowuje stanów sesji w pamięci, co czyni go odpornym na ataki typu Session Hijacking. Tożsamość jest weryfikowana na podstawie podpisanego kryptograficznie tokenu JWT przesyłanego w nagłówku `Authorization: Bearer <token>`.
*   **Polityka CORS (Cross-Origin Resource Sharing):** W pliku `main.py` skonfigurowano middleware CORS (`CORSMiddleware`). Pozwala to na określenie, jakie domeny (np. adres produkcyjny frontendu w Azure) mogą komunikować się z API, blokując próby zapytań z niezaufanych witryn.
*   **Podział ról (Role-Based Access Control - RBAC):** Uwierzytelnieni użytkownicy są weryfikowani pod kątem uprawnień w punktach wejścia (FastAPI dependencies):
    *   `admin` - pełne prawa (np. modyfikacja lig, usuwanie kont).
    *   `coach` - uprawnienia ograniczone do danej drużyny (np. dodawanie zawodników tylko do drużyny powiązanej z jego kontem: `current_user.team_id == player.team_id`).
    *   `user` - wyłącznie odczyt danych statystycznych.

---

## 5. Baza danych: Poziomy izolacji transakcji oraz zabezpieczenia przed podatnościami

### Projekt poziomów izolacji transakcji
W celu zagwarantowania spójności danych przy jednoczesnym zachowaniu wysokiej wydajności systemu, zaprojektowano następujące zasady izolacji transakcji PostgreSQL:

1.  **Domyślny poziom izolacji: `READ COMMITTED`**
    *   Jest to standardowy poziom izolacji PostgreSQL, używany dla większości operacji odczytu i prostych zapisów.
    *   **Zaleta:** Całkowicie zapobiega zjawisku „brudnego odczytu” (Dirty Reads) – transakcja widzi wyłącznie dane zatwierdzone (zacommitowane) przez inne transakcje. Zapewnia to maksymalną współbieżność i bardzo niski narzut na blokowanie wierszy.
2.  **Zapobieganie anomaliom zapisu (np. limit zawodników w drużynie, przydzielanie wyniku)**
    *   *Problem:* Podczas jednoczesnego dodawania gracza przez dwóch różnych trenerów do tej samej drużyny, na poziomie `READ COMMITTED` może dojść do sytuacji, w której obie transakcje jednocześnie policzą liczbę graczy (np. 24) i obie zatwierdzą dodanie nowego zawodnika, przekraczając twardy limit 25 zawodników (anomalia typu Phantom Read).
    *   *Rozwiązanie:* W krytycznych transakcjach zapisu (np. walidacja liczby graczy w `create_player` oraz minimalnej liczby 11 graczy w `create_game`), system stosuje blokowanie pesymistyczne na poziomie aplikacji. Wykorzystywane jest zapytanie SQLAlchemy z klauzulą `with_for_update()`, co blokuje wybrane wiersze tabeli `teams` do momentu zakończenia transakcji:
        ```python
        # Koncepcyjne zablokowanie rekordu drużyny na czas dodawania zawodnika
        stmt = select(models.Team).filter(models.Team.id == team_id).with_for_update()
        ```
    *   Dzięki temu konkurencyjna transakcja próbująca zmodyfikować tę samą drużynę musi zaczekać, gwarantując spójność reguły biznesowej.

### Zabezpieczenie przed podatnościami bazodanowymi
*   **SQL Injection (Wstrzykiwanie kodu SQL):**
    *   *Zagrożenie:* Próba podania złośliwego ciągu znaków w formularzu (np. w nazwie zawodnika) mająca na celu wykonanie nieautoryzowanego zapytania do bazy.
    *   *Zabezpieczenie:* System jest w 100% odporny na SQL Injection dzięki wykorzystaniu SQLAlchemy ORM i zapytań parametryzowanych. Wszelkie wartości zmiennych (np. nazwisko gracza czy ID ligi) nie są wklejane jako ciągi tekstowe (string concatenation), lecz są przesyłane do silnika bazy danych jako bezpieczne parametry (bind parameters). Silnik PostgreSQL traktuje je wyłącznie jako wartości danych, a nie instrukcje SQL.
*   **Integralność i spójność relacji bazy danych:**
    *   Użycie twardych więzów integralności na poziomie schematu PostgreSQL (`ForeignKey`, `nullable=False`) zapobiega powstawaniu „osieroconych” rekordów (np. gole bez przypisanego meczu).
    *   Obsługa błędów spójności (`IntegrityError`) w `crud.py` – w przypadku próby usunięcia obiektu powiązanego relacją (np. usunięcie ligi posiadającej przypisane drużyny), transakcja jest natychmiast wycofywana (`await db.rollback()`), a użytkownik otrzymuje czytelny komunikat błędu (HTTP 400), zamiast uszkodzenia struktury danych.

---

## 6. Projekt interfejsu GUI (Decyzje, przejrzystość i efektywność)

Wygląd i ergonomia interfejsu użytkownika zostały zaprojektowane z myślą o czytelności danych sportowych oraz wywarciu na użytkowniku wrażenia obcowania z systemem klasy premium.

### Decyzje projektowe dotyczące GUI:
1.  **Estetyka Glassmorphism (Szklany interfejs):**
    *   Panele informacyjne (`.glass-panel`) posiadają półprzezroczyste tła `rgba(30, 41, 59, 0.7)` oraz rozmycie tła za pomocą właściwości CSS `backdrop-filter: blur(12px)`.
    *   Styl ten nadaje aplikacji nowoczesny, trójwymiarowy wygląd, przypominający nowoczesne systemy operacyjne (macOS, Windows 11 Fluent Design).
2.  **Paleta barw Dark Mode (Tryb Ciemny):**
    *   Baza kolorystyczna opiera się na głębokim granacie/czerni (`#0f172a`), co zmniejsza zmęczenie oczu podczas analizowania statystyk.
    *   Akcenty kolorystyczne zrealizowano za pomocą żywych gradientów przechodzących od błękitu do fioletu (`linear-gradient(135deg, #3b82f6, #8b5cf6)`).
    *   Złoty kolor (`#eab308`) został zarezerwowany dla wyróżnienia najlepszych strzelców, a czerwony (`#ef4444`) sygnalizuje sekcję rywali (*Nemesis*), co natychmiast przyciąga uwagę użytkownika do kluczowych informacji.
3.  **Typografia Premium:**
    *   Zamiast domyślnych czcionek systemowych, zaimportowano nowoczesny krój pisma **Outfit** z biblioteki Google Fonts. Charakteryzuje się on doskonałą czytelnością zarówno w małych tabelach danych, jak i w dużych nagłówkach analitycznych.

### Narzędzia i techniki zapewniające przejrzystość i efektywność interakcji:
*   **Ikony Semantyczne (Lucide React):** Zastosowanie zestawu ikon Lucide (np. `Trophy` dla liderów tabeli, `Star` dla strzelców, `ShieldAlert` dla analizy zagrożeń) pozwala na natychmiastową, intuicyjną orientację w przeznaczeniu danej sekcji bez konieczności czytania etykiet tekstowych.
*   **Mikroanimacje i Interakcje (Micro-animations):**
    *   Przyciski i panele reagują na najechanie kursorem myszy (`:hover`). Panele delikatnie rozświetlają swoje krawędzie (`box-shadow: 0 0 20px rgba(59, 130, 246, 0.15)`), a przyciski główne lekko unoszą się w górę (`transform: translateY(-2px)`).
    *   Płynne przejścia (`transition: all 0.3s ease`) sprawiają, że system reaguje na akcje użytkownika w sposób naturalny i elastyczny.
*   **Szybkość i Responsywność:**
    *   Dzięki użyciu technologii React i asynchronicznego pobierania danych, przełączanie widoków oraz filtrowanie analizy rywali odbywa się bez przeładowywania całej strony.
    *   Responsywny grid CSS (`grid-template-columns: repeat(auto-fit, minmax(300px, 1fr))`) automatycznie dopasowuje układ paneli Dashboardu do ekranów laptopów, tabletów oraz telefonów komórkowych, zachowując czytelność tabel sportowych.
