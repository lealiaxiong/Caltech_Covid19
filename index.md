---
layout: default
---

<html lang="en">
     <body>
         <script src="https://code.jquery.com/jquery-3.5.0.js"></script>
         <script> 
             $(function(){
               $("#weeklyTotal").load("covid_cases_la_caltech_weekly_whole_pandemic_tag.html"); 
             });
         </script> 
         
         Total weekly cases at Caltech

         <div id="weeklyTotal"></div>
         
         <p>
             The y-axes were chosen such that the maximum weekly total of Caltech cases, 
             7-day rolling average of Caltech cases, and 7-day rolling average of LA County cases appear 
             as the same height.
         </p>
         
         <p>
             In the winter 2020/2021 surge and summer 2021 Delta surge, Caltech was either not 
             as affected as in the winter 2021/2022 Omicron surge, or we weren't testing as much 
             as we are currently.
         </p>
         
         <p>
             In April 2022, Caltech is experiencing a surge that exceeds the trend seen in the general 
             LA County population, likely driven by students returning from spring break.
         </p>

    </body>
</html>