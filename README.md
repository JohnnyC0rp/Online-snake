# Online-snake

This is online snake game on python! Just classic snake game but with multiplayer.

**Cons:**

- It uses TCP protocol which is not the best choice for online games
- *All* logic is calculated on the client side, which says "Come on, cheating is welcome". Just cut out collision checking code and only your snke will become immortal
- No encryption
- It is just a bit modified version of chat room
- Things are so bad, that speed of each snake can be easily changed by fps option in config.py. If you increase your fps, you will move faster than your opponents and they will see some kind of lagging
- Synchronisation troubles after moving windows (This can be easily fixed, but it works fun)
- Color is generated randomly, it means you can be become invisible with some chance

**Pros:**

- It works

Some screenshots:
![image](https://user-images.githubusercontent.com/79414726/224257831-cce85dde-f837-49a6-b336-409de1ed50e7.png)
![image](https://user-images.githubusercontent.com/79414726/224258158-c9fe6134-ffdc-4a06-b9a3-b6ccac33945c.png)
