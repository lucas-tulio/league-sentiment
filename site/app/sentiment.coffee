module.exports = class Sentiment

  constructor: ->
    @bars = $(".bar")
    @maxBarWidth = 300

  init: ->
    chartCanvas = $("#trending-chart")
    ctx = chartCanvas.get(0).getContext("2d")

    values = chartCanvas.data("values")
    listOfValues = values.split(";")
    pos = listOfValues[0] * 1
    neg = listOfValues[1] * -1
    total = pos + neg

    donutData = [
      {
        value: Math.round((neg / total) * 100),
        color: "#DA153F",
        label: "Negative"
      },
      {
        value: Math.round((pos / total) * 100),
        color: "#3CD9B4",
        label: "Positive"
      }
    ]

    donutOptions = {
      segmentShowStroke: false,
      segmentStrokeColor: "#fff",
      segmentStrokeWidth: 2,
      percentageInnerCutout: 50,
      animation: true,
      animationSteps: 100,
      animationEasing: "easeOutQuint",
      animateRotate: true,
      animateScale: false,
      tooltipFillColor: "rgba(0, 0, 0, 0.6)",
      tooltipTitleFontFamily: "Helvetica, sans-serif",
      animateScale : false,
      legendTemplate : "<ul class=\"<%=name.toLowerCase()%>-legend\"><% for (var i=0; i<segments.length; i++){%><li><span style=\"background-color:<%=segments[i].fillColor%>\"></span><%if(segments[i].label){%><%=segments[i].label%><%}%></li><%}%></ul>"
    }

    trendingChart = new Chart(ctx).Doughnut(donutData, donutOptions)

    # Scroll triggered animations
    $(window).bind "scroll", (e) =>
      @scrollControl()

    # Initial animation trigger for large screens
    @scrollControl()

  scrollControl: ->
    scrolledY = $(window).scrollTop()
    windowHeight = $(window).height()
    for b in @bars
      bar = $(b)
      if bar.position().top < scrolledY + windowHeight - 40
        barWidth = bar.data("value")
        barWidth *= -1 if barWidth < 0
        barWidth = @maxBarWidth if barWidth > @maxBarWidth
        bar.css {
          width: barWidth
        }
