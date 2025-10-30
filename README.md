# PBD-cinema-database  
  
### Instrukcja (jeśli ktoś potrzebuje):  
    
1. Sklonowanie - __git clone__ - zdalnego repo (czyli tego na github) na swój komp/laptop. IMO najlepiej poruszać się w Git Bash jako terminal.  
     
   Wystarczy taka komenda w folderze, gdzie chcę się sklonować repo:  
   ![alt text](<readme_pngs/p1.png>)  
     
   A link do skopiowania jak coś jest też tu: https://github.com/michal-madeiski/PBD-cinema-database.git
---
2. Po sklonowaniu można otworzyć sobie projekt (znajduje się w lokalizacji, w której było się w Bashu w momencie komendy git clone) w VS Code:  
     
   ![alt text](<readme_pngs/p2.png>)
---  
3. Projekt otwarty w VS Code - tam od razu jest dostępny terminal basha, więc resztę poleceń można robić w samym VS Code dla wygody.  
      
   Warto zaznaczyć, że domyślnie otwiera się na branchu main, czyli głównym projektowym.  
     
   ![alt text](<readme_pngs/p3.png>)  
---     
4. Aby nie było bałaganu każdy tworzy swojego brancha (najlepiej normalna nazwa żeby każdy wiedział co czyje jest):  
     
   __git checkout -b NAZWA__ np.: git checkout -b kamionka  
---     
5. Wypchnięcie brancha na github:  
      
    git add .  
    git commit -m "Branch initial commit"  
    git push -u origin kamionka  

    Ostatnia komenda powoduje, że każda następna zmiana z tego brancha może trafić na github jedynie za pomocą komendy: "git push".  
---      
6. Dodatkowe info:  
     
   __git status__ - polecenie do sprawdzenia różnic między lokalną a zdalną wersją projektu (brancha)  
   __git pull__ - pobranie ze zdalnego repo na lokalne  
   __git push__ - wypchnięcie z lokalnego repo na zdalne  