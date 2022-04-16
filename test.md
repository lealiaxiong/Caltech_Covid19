---
layout: default
---

<html lang="en">
    <head>
        <link rel="stylesheet" href="style.css">
    </head>
    <body>
        <script src="https://code.jquery.com/jquery-3.5.0.js"></script>
        <h1> Hi! If you've arrived here, you're in the wrong place. </h1>
        <p> Return to <a href="https://lealiaxiong.github.io/caltech_covid19/"> main page </a>.
             
        <div class="switch-button">
            <input class="switch-button-checkbox" type="checkbox"> id="whichPlot" onclick="switchPlot(this)"/>
            <label class="switch-button-label" for=""><span class="switch-button-label-span">weekly cases</span></label>
        </div>         
        
        <script> 
             $(function(){
               $("#weeklyTotal").load("covid_cases_la_caltech_weekly_whole_pandemic_tag.html"); 
             });
        </script> 
        <script> 
             $(function(){
               $("#dailyCases").load("covid_cases_la_caltech_daily_90_days.html"); 
             });
        </script>
        
        <script type="text/javascript">
            function switchPlot(whichPlot) {
                var weeklyTotal = document.getElementById("weeklyTotal");
                weeklyTotal.style.display = whichPlot.checked ? "none" : "block";
                var dailyCases = document.getElementById("dailyCases");
                dailyCases.style.display = whichPlot.checked ? "block" : "none";
            }
        </script>

        <div id="weeklyTotal" style="display: block"></div>
        <div id="dailyCases" style="display: none"></div>
         
        <p>
             In the weekly cases view, the y-axes were chosen such that the maximum weekly total of Caltech cases, 
             7-day rolling average of Caltech cases, and 7-day rolling average of LA County cases appear 
             as the same height.
        </p>
         
         <p>
             Based on this view, in the winter 2020/2021 surge and summer 2021 Delta surge, Caltech was either not 
             as affected as in the winter 2021/2022 Omicron surge, or we weren't testing as much 
             as we are currently.
         </p>
         
         <p>
             In April 2022, Caltech is experiencing a surge that exceeds the trend seen in the general 
             LA County population, likely driven by students returning from spring break.
         </p>
        
        <p>
            To see the daily case counts for the last 90 days, please use the toggle. Place the mouse cursor over the x-axis and scroll to view other dates.
         
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