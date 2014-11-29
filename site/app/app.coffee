Sentiment = require "sentiment"

module.exports = class App
  constructor: ->
    @sentiment = new Sentiment

  init: ->
    @sentiment.init()
