<!DOCTYPE html>
<!--[if lt IE 7]>    <html class="no-js lt-ie9 lt-ie8 lt-ie7"> <![endif]-->
<!--[if IE 7]>     <html class="no-js lt-ie9 lt-ie8"> <![endif]-->
<!--[if IE 8]>     <html class="no-js lt-ie9"> <![endif]-->
<!--[if gt IE 8]><!-->

<html class="no-js"> <!--<![endif]-->

  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge,chrome=1">
    <title>League of Legends Sentiment Analysis</title>
    <meta name="description" content="">
    <meta name="tags" content="league of legends, statistics, sentiment analysis, reddit">
    <meta name="viewport" content="width=1280, target-densitydpi=device-dpi" />
    <meta name="apple-mobile-web-app-capable" content="yes"/>
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <link rel="stylesheet" href="stylesheets/main.css">
    <script src="chart.js"></script>
    <script src="javascripts/vendor/modernizr-2.6.2.min.js"></script>
  </head>
  <body class="introAnim">

    <!-- Your content -->
    <?php
        require("database.php");
        $db = new Database();

        $currentBatch = 0;
        $currentBatchResult = $db->getCurrentBatch();
        foreach($currentBatchResult as $row) {
            $currentBatch = $row[0];
        }
        $currentBatch -= 1;
        $numberOfThreads = $db->getNumberOfThreads($currentBatch);
        $trendingList = $db->getTrending($currentBatch);
        $championsList = $db->getChampions($currentBatch);
        $teamsList = $db->getTeams($currentBatch);
        $playersList = $db->getPlayers($currentBatch);
        $overall = $db->getOverallSentiment($currentBatch);

        $db->disconnect();

        $barId = 1;
        $maxBarWidth = 300;

        /*
         * The top score will define the size of all other bars
         */
        function getTopScorePosNeg($array) {
            
            $scores = array();
            
            foreach($array as $row) {
                if($row[1] != null && $row[1] != "") {
                    $scores[] = $row[1];
                }
                if($row[2] != null && $row[2] != "") {
                    $scores[] = $row[2];
                }
            }

            $topPositive = max($scores);
            $topNegative = min($scores);
            $topNegative *= -1;

            if($topPositive >= $topNegative) {
                return $topPositive;
            } else {
                return $topNegative;
            }
        }

        function getMaxScore($array) {
            $list = array();
            foreach($array as $row) {
                $list[] = $row[1];
            }
            return max($list);
        }

        function getMinScore($array) {
            $list = array();
            foreach($array as $row) {
                $list[] = $row[1];
            }
            return min($list);
        }

        function printUniBars($data, $positive, $maxBarWidth) {
            $topScore = 0;
            $barType = "";
            if($positive) {
                $topScore = getMaxScore($data);
                $barType = "loved";
            } else {
                $topScore = getMinScore($data);
                $barType = "hated";
            }
             
            foreach($data as $row) {
                $score = number_format((float)$row[1], 2, '.', '');
                $barWidth = ($score * $maxBarWidth) / $topScore;
                echo '<tr><td class="list-text top">' . trim($row[0]) . '</td><td class="list-text">'. $score . '</td><td class="bar-td"><div id="bar' . $barId . '" data-value="' . round($barWidth) . '" class="bar ' . $barType . '"></div></td></tr>';
                $barId++;
            }
        }

        function printDualBars($data, $maxBarWidth) {
            $maxScore = getTopScorePosNeg($data);
            foreach($data as $row) {
                
                // Positive bar
                $pos = number_format((float)$row[1], 2, '.', '');
                $posBarWidth = ($pos * $maxBarWidth) / $maxScore;

                $barColor = "positive";
                echo '<tr><td class="bar-td"><div id="bar' . $barId . '" data-value="' . round($posBarWidth) . '" class="bar ' . $barColor . '"></div></td><td class="list-text">'. $pos . '</td><td class="list-text">' . trim($row[0]) . '</td>';
                $barId++;

                // Negative bar
                $neg = number_format((float)$row[2], 2, '.', '');
                $negBarWidth = ($neg * $maxBarWidth) / $maxScore;

                $barColor = "negative";
                echo '<td class="list-text">'. $neg . '</td><td class="bar-td"><div id="bar' . $barId . '" data-value="' . round($negBarWidth) . '" class="bar ' . $barColor . '"></div></td></tr>';
                $barId++;
            }
        }
    ?>

    <h1>LEAGUE SENTIMENT ANALYSIS</h1>
    <h3>By using pure statistics<br/> we know what people are feeling*</h3>

    <div class="status">
        <p class="status-text">Reading <span class="numbers"><?php echo $numberOfThreads ?></span> threads from <a href="http://reddit.com/r/leagueoflegends">/r/leagueoflegends</a> in the past <span class="numbers">24</span> hours</p>
    </div>

    <!-- Trending -->
    <div class="trending-container">
        <table style="width: 800px;">
            <tr>
                <td><h2>OVERALL</h2></td>
                <td><h2>TRENDING</h2></td>
            </tr>
            <tr>
                <td style="width: 400px;">
                    <?php
                    $chartData = "";
                    foreach($overall as $row) {
                        $chartData = $row[0] . ";" . $row[1];
                    }
                    ?>
                    <canvas id="trending-chart" style="width: 300px; height: 300px; margin-left: 50px;" width="300" height="300" data-values= <?php echo '"' . $chartData . '"'; ?>></canvas>
                </td>
                <td style="width: 400px;">
                <div class="trending-list">
                    <?php
                        $i = 1;
                        foreach($trendingList as $row) {
                            echo '<div class="trending-list-container"><p class="trending-text">#' . $i . '. ' . $row[0] . '</p></div>';
                            $i++;
                        }
                    ?>
                </div>
                </td>
            </tr>
        </table>
    </div>

    <!-- Lists -->
    <div class="section-container">

      <h2>TEAMS</h2>

      <table>
        <?php
            if($teamsList) {
                printDualBars($teamsList, $maxBarWidth);
            }
        ?>
      </table>

    </div>

    <div class="section-container">

        <h2>PLAYERS</h2>

        <table>
            <?php
            if($playersList) {
                printDualBars($playersList, $maxBarWidth);
            }
        ?>
        </table>
    </div>

    <div class="section-container">

        <h2>CHAMPIONS</h2>

        <table>
            <?php
                if($championsList) {
                    printDualBars($championsList, $maxBarWidth);
                }
            ?>
        </table>
    </div>

    <!-- Footer -->
    <div class="footer">
        <p class="footer-text"><b>*This is not hard science.</b> It's a hobby project built during our free time.</p>
        <p class="footer-text">Natural Language is a very complex discipline. There are still a few problems, such as failing to identify subjects (named entities) and wrongly profiling polarity and subjectivity.
        <br/>Made with <a href="https://www.python.org/">Python</a> and <a href="http://www.nltk.org/">NLTK</a>. References:
        <br/><i>Bird, Steven, Edward Loper and Ewan Klein (2009), Natural Language Processing with Python. O’Reilly Media Inc.</i></p>
        <p class="footer-text">Sentiment Analysis by <a href="mailto:felip.gust@gmail.com">Felipe Gustavo</a> and <a href="http://twitter.com/lucasdnd">Lucas Tulio</a>.
        Design by <a href="mailto:anaterrasevero@hotmail.com">Ana Terra Severo</a></p>
    </div>

    <!-- JavaScript libraries from CDN, with local fallback -->
    <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.1/jquery.min.js"></script>
    <script>window.jQuery || document.write('<script src="javascripts/vendor/jquery-1.10.1.min.js"><\/script>')</script>

    <script src="//code.createjs.com/easeljs-0.7.0.min.js"></script>
    <script>(window.createjs && window.createjs.EaselJS) || document.write('<script src="javascripts/vendor/easeljs-0.7.0.min.js"><\/script>')</script>

    <script src="//code.createjs.com/tweenjs-0.5.0.min.js"></script>
    <script>(window.createjs && window.createjs.TweenJS) || document.write('<script src="javascripts/vendor/tweenjs-0.5.0.min.js"><\/script>')</script>

    <script src="javascripts/app.js"></script>
    <script>require('init');</script>
  </body>
</html>