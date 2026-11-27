[EN] English version first | [RO] Varianta în română mai jos

NICE GATE CHANGES (Robus 600 / ROBUSR10 control unit, firmware FG01d) – 2026-11-26
==================================================================================

Board: LilyGo T-CAN485 (ESP32), ESPHome 2026.11.1, local component my_components/bus_t4
(derived from makstech/esphome-BusT4, with own additions: send_it4_cmd, is_ready).


1. SUMMARY
----------
- The configuration register map in the component was WRONG for Robus. Fixed and verified
  by reading the values directly from the control unit.
- HA switches and numbers now read the REAL value from the control unit (no longer
  optimistic, and nothing is written to the control unit when the ESP boots).
- Added: generic parameter read (GET), "Photocell" entity (experimental), speed and force on
  the correct registers, L3 wait time, diagnostic button.
- Removed: "Peak mode" (does not exist on Robus) and the old speed/force numbers (they wrote
  to the wrong registers).


2. REGISTER MAP – VERIFIED ON ROBUSR10
--------------------------------------
Confirmed by reading (GET) and consistent with pruwait/Nice_BusT4, srepenko/Nice_BusT4
and bpietroiu/esphome-nice-bidiwifi.

  Register  Meaning                              Value read / set
  0x42      Opening speed (%)                    100 → 90
  0x43      Closing speed (%)                    100 → 90
  0x45      Slow-down speed, opening (%)         22 → 30
  0x46      Slow-down speed, closing (%)         22
  0x4A      Opening force (%)                    70
  0x4B      Closing force (%)                    70 → 50
  0x80      L1 Automatic closing                 1 (ON)
  0x81      Pause time (s)                       1 → 30
  0x84      L2 Close after photo                 1 (ON)
  0x85      Close-after-photo wait (s)           1 → 5   (value 2 is not accepted, reverts to 5)
  0x88      L3 Always close                      0 → 1 (ON)
  0x89      L3 wait before closing (s)           5
  0x8A      L3 mode (meaning not confirmed)      32 (0x20)
  0x8C      Standby                              1 (ON)
  0x94      Pre-flash                            1 (ON)
  0x82, 0x83, 0x93                               DO NOT EXIST on Robus (error response FD)

Old (wrong) map in the component and its real effect:
  - "L2" wrote 0x81      → actually the PAUSE TIME (on = 1 s, off = 0 s)
  - "L3" wrote 0x82      → non-existent register (no effect)
  - "Standby" wrote 0x83 → non-existent register (no effect)
  - "Peak" wrote 0x84    → actually L2 (off = disabled L2)
  - "Pre-Flash" wrote 0x85 → actually the close-after-photo wait time
  - "Pause duration" wrote 0x88 → actually L3 (any value > 0 enabled it)
  - "Opening/closing speed/force" wrote 0x90/0x91/0x92 → start-up settings, not speed/force
  Observed consequence: the real pause was 1 s, rewritten by the "L2" switch on every ESP boot.


3. COMPONENT CHANGES (my_components/bus_t4/cover/)
--------------------------------------------------
cover.h / cover.cpp / __init__.py

- NEW request_config(reg): GET on any register; the response is cached and logged
  ("Config 0x.. = ..", INFO on change, DEBUG when unchanged).
- NEW get_config_value(reg): last value read for any register 0x00–0xFF
  (-1 if unknown). Used from the YAML lambdas.
- NEW request_io_state(): manual GET on 0xD1 (I/O diagnostics).
- NEW periodic I/O polling (0xD1) when the photocell sensor is configured:
  1 s while the gate is not closed, 10 s while closed; no polling while moving on Robus
  (options: io_poll_interval, io_poll_interval_closed, io_poll_while_moving).
- NEW binary_sensor "photocell": configurable byte/mask (photocell_byte, default 2;
  photocell_mask, default 0x04 – the bidiwifi mapping). NOT yet confirmed on Robus.
- NEW INFO log "INF_IO changed: .." on every change of the I/O response
  (to identify the photocell bit).
- NEW optional auto_close_state / photo_close_state (binary_sensor) + configurable registers
  (default 0x80 / 0x84) and config_readback_interval. Not used in the final YAML
  (the switches read directly from the control unit).
- FIX the periodic I/O response can no longer overwrite position/state while the gate is
  moving (limit-switch confirmation only when idle or when confirmation was requested).
- The value cache (config_cache_) was extended to 256 registers (initialised in setup()).
- NEW (27.11) optional text_sensor "io_raw": the full 0xD1 response (14 bytes, hex) published to HA on
  every change so it is kept in history ("INF_IO brut" entity); the "INF_IO changed" log now shows the
  whole payload, not just 5 bytes.


4. CHANGES IN nice.yaml
-----------------------
- Switches (template, NON-optimistic, read from the control unit; write + re-read after 700 ms):
    Automatic Closing (L1)   → 0x80
    Close after Photo (L2)   → 0x84
    Always Close (L3)        → 0x88
    Standby Mode             → 0x8C
    Pre-Flash                → 0x94
- Numbers (template, read from the control unit, 5 s update; write + re-read):
    Pause Duration (s)                       → 0x81 (0–250)
    Close-after-Photo Wait (s)               → 0x85 (0–30)
    L3 Wait before Closing (s)               → 0x89 (0–250)
    Opening / Closing Speed (%)              → 0x42 / 0x43 (10–100)
    Opening / Closing Slow-down Speed (%)    → 0x45 / 0x46 (10–100)
    Opening / Closing Force (%)              → 0x4A / 0x4B (10–100)
- Diagnostic sensor "L3 Mode (raw value 0x8A)" (read-only).
- binary_sensor "Gate Photocell" (in cover: photocell) and text_sensor "INF_IO brut" (in cover: io_raw).
- Diagnostic button "Read control unit parameters" (logs all registers above + I/O).
- Automatic parameter re-read: ~15 s after boot and every 60 s (interval).
- REMOVED: "Peak Mode (Max power)" switch, the old "Opening/Closing Speed/Motor Force"
  numbers (0x90–0x92), the l1_state global, the "L1/L2 read from control unit" entities.
- REMOVED: the comment containing the WiFi SSID/password in plain text.
- Note: the ESP no longer writes anything to the control unit at boot (restore_mode/optimistic removed).


5. HOME ASSISTANT CONFIGURATION (not part of the repo, for reference)
---------------------------------------------------------------------
- "Gate Approach" zone 275 m → 290 m; Bayesian sensors aligned to 290 m (poarta.yaml).
- V10 (approach zone): L1/L2 switched off before Open&Lock, checked every 5 s while the
  gate stays open (90 s), switched back on after Unlock&Close with a 30 s check.
- NEW "Nice Gate: State check after restart" (ha_ready event): L1/L2, gate left open,
  lock state, board unavailable (notification with confirmation, repeated every 2 min).
- NEW "Nice Gate: Ensure L1/L2 on opening" (>40% open, ignores the false value at ESP boot,
  does not run while V10 is active).
- poarta.yaml: removed the old MQTT entities "Poarta Nice Robus 600" and "Stare Blocare Poarta".
- Gate dashboard: reorganised (Control / Control unit settings / Diagnostics).


6. TEST STATUS
--------------
- Parameter read/write: TESTED on ROBUSR10 (all registers in section 2).
- Photocell: TEST FAILED with the bidiwifi mapping (27.11, car passed with the gate fully open, sensor stayed
  off). The correct bit is being searched for with "INF_IO brut".
- Photocell: IDENTIFIED (27.11 evening). On a Robus with PHW photocells via IBW (BlueBUS), 0xD1 response
  byte 4 = 0x04 opening, 0x01 closing, 0x08 photocells powered and clear; bit 0x08 drops to 0 while the
  beam is interrupted. New option photocell_active_low: true (photocell_byte: 4, photocell_mask: 0x08);
  the state is only valid with the gate open or closing (with the gate closed, standby powers BlueBUS down). The 0xD1 response with the gate closed is constant
  (01 00 40 00 00 04 00 00 00 04 00 02 01 00). The photocell bit on Robus still has to be
  identified with the gate open (standby cuts power to the photocells when idle).
- Meaning of the 0x8A value (L3 mode = 32) – not confirmed.


7. SHORT TEXT FOR THE UPDATE NOTIFICATION
-----------------------------------------
Nice gate update (Robus): fixed the configuration register map (L2, L3, standby, pause,
pre-flash, speed and force were written to the wrong registers). All settings are now read
from the control unit and are no longer rewritten when the ESP boots. Added: speed / force /
slow-down on the correct registers, L3 wait time, generic parameter read, diagnostic button
and a photocell sensor (experimental). Removed: "Peak mode" and the old speed/force numbers.
WARNING: after updating, check L2, pause time and force in HA – the old values may have been
altered by the wrong map.


==================================================================================
==================================================================================

MODIFICĂRI POARTĂ NICE (Robus 600 / centrala ROBUSR10, firmware FG01d) – 26.11.2026
==================================================================================

Placă: LilyGo T-CAN485 (ESP32), ESPHome 2026.11.1, componenta locală my_components/bus_t4
(derivată din makstech/esphome-BusT4, cu adăugiri proprii: send_it4_cmd, is_ready).


1. REZUMAT
----------
- Harta registrelor de configurare din componentă era GREȘITĂ pentru Robus. Corectată și
  verificată prin citire directă din centrală.
- Switch-urile și numerele din HA citesc acum valoarea REALĂ din centrală (nu mai sunt
  optimiste și nu mai scriu nimic în centrală la pornirea ESP-ului).
- Adăugate: citirea oricărui parametru (GET), entitatea „Fotocelulă” (în test), viteză și
  forță pe registrele corecte, timpul de așteptare L3, butonul de diagnoză.
- Eliminate: „Mod Peak” (nu există pe Robus) și vechile numere de viteză/forță (scriau în
  registre greșite).


2. HARTA REGISTRELOR – VERIFICATĂ PE ROBUSR10
---------------------------------------------
Confirmată prin citire (GET) și concordantă cu pruwait/Nice_BusT4, srepenko/Nice_BusT4
și bpietroiu/esphome-nice-bidiwifi.

  Registru  Semnificație                         Valoare citită / setată
  0x42      Viteză deschidere (%)                100 → 90
  0x43      Viteză închidere (%)                 100 → 90
  0x45      Viteză încetinire deschidere (%)     22 → 30
  0x46      Viteză încetinire închidere (%)      22
  0x4A      Forță deschidere (%)                 70
  0x4B      Forță închidere (%)                  70 → 50
  0x80      L1 Închidere automată                1 (ON)
  0x81      Timp pauză (s)                       1 → 30
  0x84      L2 Închidere după foto               1 (ON)
  0x85      Așteptare după foto (s)              1 → 5   (valoarea 2 nu e acceptată, revine la 5)
  0x88      L3 Închide mereu                     0 → 1 (ON)
  0x89      L3 așteptare înainte de închidere(s) 5
  0x8A      L3 mod (semnificație neconfirmată)   32 (0x20)
  0x8C      Standby                              1 (ON)
  0x94      Pre-flash                            1 (ON)
  0x82, 0x83, 0x93                               NU EXISTĂ pe Robus (răspuns eroare FD)

Harta veche (greșită) din componentă și efectul real:
  - „L2” scria 0x81      → de fapt TIMPUL DE PAUZĂ (on = 1 s, off = 0 s)
  - „L3” scria 0x82      → registru inexistent (fără efect)
  - „Standby” scria 0x83 → registru inexistent (fără efect)
  - „Peak” scria 0x84    → de fapt L2 (off = dezactiva L2)
  - „Pre-Flash” scria 0x85 → de fapt așteptarea după foto
  - „Durată pauză” scria 0x88 → de fapt L3 (orice valoare > 0 îl pornea)
  - „Viteză deschidere/închidere/forță” scriau 0x90/0x91/0x92 → setări de pornire, nu viteză/forță
  Consecință observată: pauza reală era 1 s, rescrisă de switch-ul „L2” la fiecare boot al ESP-ului.


3. MODIFICĂRI ÎN COMPONENTĂ (my_components/bus_t4/cover/)
---------------------------------------------------------
cover.h / cover.cpp / __init__.py

- NOU request_config(reg): GET pe orice registru; răspunsul e reținut și logat
  („Config 0x.. = ..”, INFO la schimbare, DEBUG dacă e neschimbat).
- NOU get_config_value(reg): ultima valoare citită pentru orice registru 0x00–0xFF
  (-1 dacă nu e cunoscută). Folosit din lambda-urile YAML.
- NOU request_io_state(): GET manual pe 0xD1 (diagnoza I/O).
- NOU interogare periodică I/O (0xD1) dacă e configurat senzorul de fotocelulă:
  1 s cât poarta nu e închisă, 10 s cât e închisă; fără interogări în mișcare pe Robus
  (opțiuni: io_poll_interval, io_poll_interval_closed, io_poll_while_moving).
- NOU binary_sensor „photocell”: byte/mask configurabile (photocell_byte, implicit 2;
  photocell_mask, implicit 0x04 – maparea bidiwifi). NECONFIRMAT încă pe Robus.
- NOU log INFO „INF_IO changed: ..” la fiecare schimbare a răspunsului I/O
  (pentru identificarea bitului fotocelulei).
- NOU opțional auto_close_state / photo_close_state (binary_sensor) + registre configurabile
  (implicit 0x80 / 0x84) și config_readback_interval. Nefolosite în YAML-ul final
  (switch-urile citesc direct din centrală).
- FIX răspunsul I/O periodic nu mai poate suprascrie poziția/starea cât poarta e în mișcare
  (confirmarea prin capete de cursă doar în repaus sau la confirmare cerută).
- Memoria de valori (config_cache_) a fost extinsă la 256 de registre (inițializată în setup()).
- NOU (27.11) text_sensor opțional „io_raw”: răspunsul complet 0xD1 (14 octeți, hex) publicat în HA la
  fiecare schimbare, ca să rămână în istoric (entitatea „INF_IO brut”); logul „INF_IO changed” arată acum
  tot payload-ul, nu doar 5 octeți.


4. MODIFICĂRI ÎN nice.yaml
--------------------------
- Switch-uri (template, NE-optimiste, citesc din centrală; scriere + recitire după 700 ms):
    Închidere Automată (L1)  → 0x80
    Închidere după Foto (L2) → 0x84
    Închide Mereu (L3)       → 0x88
    Mod Standby              → 0x8C
    Pre-Flash                → 0x94
- Numere (template, citesc din centrală, update 5 s; scriere + recitire):
    Durată Pauză (s)                         → 0x81 (0–250)
    Așteptare după Foto (s)                  → 0x85 (0–30)
    L3 Așteptare înainte de închidere (s)    → 0x89 (0–250)
    Viteză Deschidere / Închidere (%)        → 0x42 / 0x43 (10–100)
    Viteză Încetinire Deschidere / Închidere → 0x45 / 0x46 (10–100)
    Forță Deschidere / Închidere (%)         → 0x4A / 0x4B (10–100)
- Senzor diagnostic „L3 Mod (valoare brută 0x8A)” (doar citire).
- binary_sensor „Fotocelulă Poartă” (în cover: photocell) și text_sensor „INF_IO brut” (în cover: io_raw).
- Buton diagnostic „Citește parametri centrală” (loghează toate registrele de mai sus + I/O).
- Recitire automată a parametrilor: la ~15 s după pornire și la fiecare 60 s (interval).
- ELIMINAT: switch „Mod Peak (Putere maximă)”, numerele vechi „Viteză Deschidere/Închidere/
  Forță Motor” (0x90–0x92), global l1_state, entitățile „L1/L2 citit din centrală”.
- ELIMINAT: comentariul cu SSID/parola WiFi în clar.
- Notă: ESP-ul nu mai scrie nimic în centrală la boot (restore_mode/optimistic eliminate).


5. CONFIGURAȚIE HOME ASSISTANT (nu ține de repo, pentru referință)
------------------------------------------------------------------
- Zona „Apropiere Poartă” 275 m → 290 m; senzorii Bayesian aliniați la 290 m (poarta.yaml).
- V10 (zona de apropiere): L1/L2 oprite înainte de Deschide&Blochează, verificate la 5 s cât
  poarta stă deschisă (90 s), repornite după Deblochează&Închide cu verificare la 30 s.
- NOU „Poartă Nice: Verificare stare după restart” (event ha_ready): L1/L2, poartă rămasă
  deschisă, stare blocare, placă indisponibilă (notificare cu confirmare, repetată la 2 min).
- NOU „Poartă Nice: Asigură L1/L2 la deschidere” (>40% deschidere, ignoră valoarea falsă de la
  boot-ul ESP, nu rulează cât V10 e activ).
- poarta.yaml: eliminate entitățile MQTT vechi „Poarta Nice Robus 600” și „Stare Blocare Poarta”.
- Dashboard Poarta: reorganizat (Control / Setări centrală / Diagnostic).


6. STATUS TESTARE
-----------------
- Citire/scriere parametri: TESTAT pe ROBUSR10 (toate registrele din secțiunea 2).
- Fotocelulă: TEST EȘUAT cu maparea bidiwifi (27.11, trecere cu poarta deschisă, senzorul a rămas off).
  Bitul corect se caută cu „INF_IO brut”.
- Fotocelulă: IDENTIFICATĂ (27.11 seara). Pe Robus cu fotocelule PHW prin IBW (BlueBUS), răspunsul 0xD1
  octetul 4 = 0x04 deschidere, 0x01 închidere, 0x08 fotocelule alimentate și libere; bitul 0x08 cade la 0
  cât fasciculul e întrerupt. Opțiune nouă photocell_active_low: true (photocell_byte: 4, photocell_mask: 0x08);
  starea e validă doar cu poarta deschisă sau în închidere (cu poarta închisă, standby oprește BlueBUS). Răspunsul 0xD1 cu poarta închisă e constant
  (01 00 40 00 00 04 00 00 00 04 00 02 01 00). Bitul fotocelulei pe Robus urmează să fie
  identificat cu poarta deschisă (standby oprește alimentarea fotocelulelor în repaus).
- Semnificația valorii 0x8A (L3 mod = 32) – neconfirmată.


7. TEXT SCURT PENTRU NOTIFICAREA DE UPDATE
------------------------------------------
Update poartă Nice (Robus): corectată harta registrelor de configurare (L2, L3, standby,
pauză, pre-flash, viteză, forță scriau în registre greșite). Toate setările se citesc acum din
centrală și nu se mai rescriu la pornirea ESP-ului. Adăugate: viteză/forță/încetinire pe
registrele corecte, timp de așteptare L3, citire generică a parametrilor, buton de diagnoză și
senzor de fotocelulă (experimental). Eliminate: „Mod Peak” și vechile numere de viteză/forță.
ATENȚIE: după update, verificați L2, pauza și forța în HA – valorile vechi pot să fi fost
alterate de harta greșită.
