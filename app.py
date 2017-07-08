from flask import Flask
from flask import redirect
from flask import session
from flask import request
from flask import url_for
from flask import render_template
import datetime
import requests
import md5
import requests
import json
from activecampaign.client import ActiveCampaignClient
from activeCampaign.Config import ACTIVECAMPAIGN_URL, ACTIVECAMPAIGN_API_KEY
from twilio.rest import Client
from slotbot import get_slots
from googbot import authorize_cal
import cgi

app = Flask(__name__)
app.secret_key = '3d53393efa2592e93ef624f15cdbf478'
account_sid = "AC5ce745d0938bc623da858b85d35b4044"
auth_token = "be67c94ff541fe8382dea7080152f0d2"

#TESTING 

INFO_REQUEST_URL = "https://www.fulfilleddesires.net//SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=book-appointment"
NEW_CUSTOMER_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=customer&identifier=new"
DAILY_TASK_URL = "https://www.fulfilleddesires.net/SALVAGE_SITE_WEB/AU/hookme/REST-CSConnector.awp?thingie=create-task"

app.config['SESSION_TYPE'] = 'filesystem'
dateTimeFormat = "%Y-%m-%dT%H:%M:%S.%fZ"
prettyFormat = "%A %d %b at %H:%M"

@app.route('/')
def test():
	return '<div class="_form_9"></div><script src="https://skillionbikes.activehosted.com/f/embed.php?id=9" type="text/javascript" charset="utf-8"></script>'

@app.route('/api/v2/subscribe', methods = ["POST"])
def subscribeThing():
	first_name = request.form['contact[first_name]']
	last_name = request.form['contact[last_name]']
	email = request.form['contact[email]']
	countrycode = request.form['contact[fields][country_telephone_code]']
	number = request.form['contact[phone]']
	dob = request.form['contact[fields][date_of_birth]']

	headers = {'content-type': 'application/json'}
	payload = {}
	payload["customer"] = {"name_first": first_name, "name_last": last_name, "email": email,
		"mobile_phone_country_cd": countrycode, "mobile_phone_number": number,
		"dob": dob, "timezone": "Australia/Sydney"}
	print "\n\n-----------\n\n"
	print "Payload for subscribe accepted"
	print payload
	print "\n\n-----------\n\n"
	r = requests.post(NEW_CUSTOMER_URL, data=json.dumps(payload), headers=headers)
	print "\n\n-----------\n\n"
	print "Response for subscribe accepted"
	print str(r.content)
	print "\n\n-----------\n\n"
	try:
		URL = "https://app.bombbomb.com/app/api/api.php?method=SendEmailToEmailAddress&email=nate@skillionbikes.com&pw=Skillion102&email_id=%s&email_address=%s" % ( "46264c5b-e4f8-25f5-9cc7-6f6c745c73d0", email )
		r = requests.get(URL)
		print "BombBomb email sent"
	except:
		pass
	return "200"

@app.route('/api/v2/sms1', methods = ["POST"])
def sendSMS1():
	phone = request.form['contact[phone]']
	firstname = request.form['contact[first_name]']
	body = "Hey %s! Nate here from Skillion. Just seen you're \
	interested in our bikes. Fancy a test ride of one? Text me back YES if you're\
	keen!" % firstname
	client = Client(account_sid, auth_token)
	message = client.messages.create(to=phone, from_="+61436434400",
		body=body)
	return "200"

@app.route('/api/v2/receive', methods = ["GET", "POST"])
def recSMS1():
	import json
	number = request.form['From']
	send_Number = number.replace('+', '00')
	message_body = request.form['Body']
	AC_client = ActiveCampaignClient(ACTIVECAMPAIGN_URL, ACTIVECAMPAIGN_API_KEY)
	slots = get_slots()
	prettySlots = []
	print "\n\nInbound SMS reads --" + message_body.lower()
	for slot in slots:
		temp = datetime.datetime.strptime(slot, dateTimeFormat)
		prettySlots.append(temp.strftime(prettyFormat))
	if message_body.lower() == "yes":
		body = "Text 1 for %s. Text 2 for %s. Text 3 for neither!" % (prettySlots[0], prettySlots[-1])
		client = Client(account_sid, auth_token)
		message = client.messages.create(to=number, from_="+61436434400", body=body)
		return "200"
	elif message_body.lower() == "1":
		headers = {'content-type': 'application/json', 'x-ayfkm': 'SOMESHIT'}
		payload = { "mobile_number": send_Number, "appointment": get_slots()[0]}
		print "\nPAYLOAD"
		print payload
		r = requests.post(INFO_REQUEST_URL, data=json.dumps(payload), headers=headers)
		response = json.loads(r.content)
		print "\n"
		print response
		print "this is the response"
		print "\n"
		if str(response['Status']['Successful']) == "True":
			getName = json.loads(r.content)['requested_info']['first_name']
			body = "AWESOME! I'll see you %s for your test ride, %s! Nate" % (prettySlots[0], getName)
			client = Client(account_sid, auth_token)
			message = client.messages.create(to=number, from_="+61436434400", body=body)
			email = json.loads(r.content)['requested_info']['email']
			AC_client.contacts.tag_remove("[SMS2_NOT_RESPONDED]", email=email)
			return "200"
		else:
			first_name = response['has_appointment']['name_first']
			slot = response['has_appointment']['commencing_date'].replace('-', ' ') + "at" + response['has_appointment']['commencing_time']
			body = "Hey %s! Just checked and you're already booked in for a test ride on %s :)" % (first_name, slot)
			client = Client(account_sid, auth_token)
			message = client.messages.create(to=number, from_="+61436434400", body=body)
			return "200"
	elif message_body.lower() == "2":
		headers = {'content-type': 'application/json', 'x-ayfkm': 'SOMESHIT'}
		payload = { "mobile_number": send_Number,
		    "appointment": get_slots()[-1]}
		r = requests.post(INFO_REQUEST_URL, data=json.dumps(payload), headers=headers)
		response = json.loads(r.content)
		print payload
		print "\n"
		print response
		if str(response['Status']['Successful']) == "True":
			email = json.loads(r.content)['requested_info']['email']
			getName = json.loads(r.content)['requested_info']['first_name']
			body = "AWESOME! I'll see you %s for your test ride, %s! Nate" % (prettySlots[-1], getName)
			client = Client(account_sid, auth_token)
			message = client.messages.create(to=number, from_="+61436434400", body=body)
			AC_client.contacts.tag_remove("[SMS2_NOT_RESPONDED]", email=email)
			return "200"
		else:
			first_name = response['has_appointment']['name_first']
			slot = response['has_appointment']['commencing_date'].replace('-', ' ') + "at" + response['has_appointment']['commencing_time']
			body = "Hey %s! Just checked and you're already booked in for a test ride on %s :)" % (first_name, slot)
			client = Client(account_sid, auth_token)
			message = client.messages.create(to=number, from_="+61436434400", body=body)
			return "200"
	elif message_body.lower() == "3":
		headers = {'content-type': 'application/json'}
		payload = {}
		payload["daily_task"] = {
			"mobile_number": send_Number,
			"task_detail":"Call Task"}
		r = requests.post(DAILY_TASK_URL, data=json.dumps(payload), headers=headers)
		print payload
		print str(json.loads(r.content))
		getName = json.loads(r.content)['daily_task']['name_first']
		body = "No worries, %s! Let me or Peter call you and organise a better time for you over the next few days :)" % getName
		client = Client(account_sid, auth_token)
		message = client.messages.create(to=number, from_="+61436434400", body=body)
		return "200"
	else:
		return "200"

@app.route('/api/v2/email', methods = ["POST"])
def sendEmail1():
	firstname = request.form['contact[first_name]']
	email = request.form['contact[email]']
	phone = request.form['contact[phone]']
	send_Number = request.form['contact[fields][country_telephone_code]'] + phone
	print "send number is " + send_Number
	link1 = "http://138.197.33.106/book/" + send_Number + "/1"
	link2 = "http://138.197.33.106/book/" + send_Number + "/2"
	link3 = "http://138.197.33.106/book/" + send_Number + "/3"
	slots = get_slots()
	prettySlots = []
	for slot in slots:
		temp = datetime.datetime.strptime(slot, dateTimeFormat)
		prettySlots.append(temp.strftime(prettyFormat))
	message = render_template('email.html', name = firstname, slot1Link = link1, slot1 = str(prettySlots[0]), slot2Link = link2, slot2 = str(prettySlots[-1]), slot3Link = link3)
	response = requests.post("https://api.mailgun.net/v3/spyryl.info/messages",
        auth=("api", "key-727fa624b0c5d1c7f224016a6047d936"),
        data={"from": "Skillion Team <info@skillion.com.au>",
              "to": [email],
              "subject": "Skillion Test Ride",
              "html": message})
	return "200"

@app.route('/book/<phone>/<slotno>')
def emailBook(phone, slotno):
	import json
	headers = {'content-type': 'application/json', 'x-ayfkm': 'SOMESHIT'}
	if int(slotno) == 1:
		payload = { "mobile_number": phone, "appointment": get_slots()[0]}
		print payload
		r = requests.post(INFO_REQUEST_URL, data=json.dumps(payload), headers=headers)
		print str(json.loads(r.content))
	elif int(slotno) == 2:
		payload = { "mobile_number": phone, "appointment": get_slots()[-1]}
		r = requests.post(INFO_REQUEST_URL, data=json.dumps(payload), headers=headers)
		print str(json.loads(r.content))
	else:
		headers = {'content-type': 'application/json'}
		payload = {}
		payload["daily_task"] = {
			"mobile_number": phone,
			"task_detail":"Call Task"}
		print payload
		r = requests.post(DAILY_TASK_URL, data=json.dumps(payload), headers=headers)
		print str(json.loads(r.content))
		getName = json.loads(r.content)['daily_task']['name_first']
		body = "No worries, %s! Let me or Peter call you and organise a better time for you over the next few days :)" % getName
		return body
	return "Appointment confirmed"

@app.route('/api/v2/event', methods = ["GET"])
def makeEvent():
	email = request.args.get('email')
	fromDate = request.args.get('fromDate')
	toDate = request.args.get('toDate')
	desc = request.args.get('desc')
	address = request.args.get('address')

	event = {
	  'summary': email,
	  'location': address,
	  'description': desc,
	  'start': {
		'dateTime': fromDate,
		'timeZone': 'Australia/Sydney',
	  },
	  'end': {
		'dateTime': toDate,
		'timeZone': 'Australia/Sydney',
	  },
	  'attendees': [
		{'email': email},
		{'email': 'pete@skillionbikes.com'},
	  ],
	  'reminders': {
		'useDefault': False,
		'overrides': [
		  {'method': 'email', 'minutes': 24 * 60},
		  {'method': 'popup', 'minutes': 10},
		],
	  },
	}
	service = authorize_cal()
	event = service.events().insert(calendarId='primary', body=event).execute()
	return json.dumps({'EventLink' : event.get('htmlLink')})

if __name__ == "__main__":
    app.run(debug=True)
