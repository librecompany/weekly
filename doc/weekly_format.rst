Formato del weekly
''''''''''''''''''

:Authors: Simone Basso <bassosimone@gmail.com>
:Version: 1.2 of 2013-04-11

.. Nota: questo file si puo` trasformare in `html` usando il
   comando ``rst2html doc/weekly_format.rst``

In principio ci sono i progetti e le attivita`.

**Progetti**
  Portano soldi, quindi li indichiamo con il dollaro (e.g. `$lapsi`).

**Attivita**
  Occupano una percentuale del tempo, quindi usiamo il percento per
  indicarle (e.g. `%ricerca`)

Ogni `entry` del weekly dovrebbe essere a proposito dell'intersezione tra
un `$progetto` e una `%attivita`::

  Ho lavorato allo %sviluppo di $neubot.

Indicare sempre il tempo dedicato all'intersezione tra progetto e
attivita` (d = giorno, h = ora). Il tempo va indicato tra quadre in
fondo alla riga; e.g.::

  Ho lavorato alla %rendicontazione di $evpsi [10h].

Si possono usare liberamente i `#tag` e gli `@handle`, come in Twitter. Anche
se stiamo cercando di convergere verso un set di `#tag` e `@handle` noti.

Tra una entry e l'altra ci *deve* essere una riga vuota.

Una riga standard del weekly ha grosso modo il seguente significato::

  (io, sottinteso) ho fatto una certa %attivita, eventualmente specificata
  in #qualcheModo, riguardo al $progetto, interagendo o collaborando con
  @qualchePersona e/o @qualcheIstituzione per [tempo].

Quando il software di gestione del weekly incontra una riga che contiene
solo la parola `TODO` oppure solo `--`, tutto quello che segue quella
riga viene ignorato.


