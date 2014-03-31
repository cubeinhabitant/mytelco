Mytelco is a rest service to provide call handling commands to Twilio. This
application is an example. It was designed to run on a Google App Engine.
An overview of this application can be found in my blog post
"[Cutting the landline phone](http://www.jpeterson.com/2014/03/30/cutting-the-landline-phone/)".



Helpful local testing:

* curl --verbose --data @test/resource/incomingCall.txt http://localhost:8080/twiml/incomingCall
* curl --verbose --data @test/resource/choiceSelection.txt http://localhost:8080/twiml/choiceSelection
* curl --verbose --data @test/resource/callEnd.txt http://localhost:8080/twiml/callEnd
* curl --verbose --data @test/resource/callEnd-noAnswer.txt http://localhost:8080/twiml/callEnd
* curl --verbose --data @test/resource/voicemail.txt http://localhost:8080/twiml/voicemail