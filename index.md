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
         
         <h1>Total weekly cases at Caltech</h1>

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
         
         <h2>Data sources</h2>
         
         <p>
             Caltech data transcribed manually from: https://together.caltech.edu/cases-testing-and-tracing/case-log.
             Omitted cases where people lived out of state and had never accessed campus. 
             Date indicates the date that a case was posted on the case log (not the date the people tested positive). CCC indicates
             Caltech Childcare Center.
         </p>
         
         <p>
             LA County data sourced from NY Times Github. Data with rolling averages can be found at: 
             https://github.com/nytimes/covid-19-data/tree/master/rolling-averages (as of 2022-04-15). 
         </p>
         <p>
             The data is split between .csv files by year. Raw files are found at:
         </p>
         <ul>
                <li>https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-2020.csv</li>
                <li>https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-2021.csv</li>
                <li>https://raw.githubusercontent.com/nytimes/covid-19-data/master/rolling-averages/us-counties-2022.csv</li>
         </ul>

    </body>
</html>