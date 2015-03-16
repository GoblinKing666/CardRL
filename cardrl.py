import pygame
import os
import math
import eztext


FRAMERATE = 60.0
NO_EASE = 0
SLIDE_EASE = 1
POSITION_TWEEN = 0
SIZE_TWEEN = 1
ROTATION_TWEEN = 2
COLOR_TWEEN = 3
IN_HAND = 0
HAND_ZOOMED = 1
ZOOMED = 2
MENU_OPTION = 3



def initiateCCDB(path):
	global allcc
	allcc = {}
	from lxml import etree
	ccoptions = open(path)
	races = {}
	classes = {}
	t1 = {}
	t1key = ""
	t2 = []
	t2key = ""
	reading_in = ""
	for event, element in etree.iterparse(ccoptions, events=("start","end")):
		if event=="start":
			if element.tag=="races":
				reading_in = "race"
			elif element.tag=="classes":
				reading_in = "class"
			elif element.tag=="category":
				t1 = {}
				t1key = element.get("name")
			elif element.tag=="race" or element.tag=="class":
				t2 = []
				t2key = element.get("name")
			elif element.tag=="card":
				amt = element.get("amt")
				name = element.text
				t2.append((name,amt))
		elif event=="end":
			if element.tag=="category":
				if reading_in=="race":
					races[t1key] = t1
				elif reading_in=="class":
					classes[t1key] = t1
			elif element.tag=="race" or element.tag=="class":
				t1[t2key] = t2
	allcc["Races"] = races
	allcc["Classes"] = classes



def getCardByName(name):
	global cardnitty
	return Card().copy(cardnitty[name])


def initiateCardDB(path):
	global allcards
	global cardnitty
	allcards = {}
	cardnitty = {}
	from lxml import etree
	cardset = open(path)
	carddata = {'name':"NAME",'cardtype':"TYPE",'subtype':"SUBTYPE",'text':"TEXT",'cost':0,'hp':0}
	for event, element in etree.iterparse(cardset, events=("start","end")):
		if event=="start":
			carddata[element.tag] = element.text
			print element.tag + '->' + element.text
			print element.tag + ' has become ' + carddata[element.tag]
		else:
			if element.tag=="card":
				allcards[len(allcards)] = Card(carddata['name'],carddata['cost'],carddata['cardtype'].strip(),carddata['subtype'],carddata['text'],carddata['hp'])
				cardnitty[carddata['name']] = allcards[len(allcards)-1]
				carddata = {'name':"",'cardtype':"",'subtype':"",'text':"",'cost':0,'hp':0}



def clamp(value, mind, maxd):
	return max(min(value, maxd), mind)

def smoothstep(edge0, edge1, x):
	x = clamp((x - edge0)/(edge1-edge0),0.0,1.0)
	return x*x*(3 - 2*x)


class TweenHelper():
	sprite = None
	start = (0,0)
	end = (0,0)
	current = (0,0)
	time = 0
	elapsed = 0
	rise = 0
	run = 0
	easetype = 0
	steps = 0
	tweentype = 0
	def __init__(self,sp,tt,en,ti,et):
		self.sprite = sp
		self.end = en
		self.time = ti
		if tt==POSITION_TWEEN:
			self.start = self.sprite.rect.center
		elif tt==SIZE_TWEEN:
			self.start = self.sprite.rect.size
		elif tt==COLOR_TWEEN:
			self.start = self.sprite.color
		self.current = self.start
		self.easetype = et
		self.tweentype=tt
	def step(self,seconds):
		

		#max(min(my_value, max_value), min_value)

		self.steps += 1
		
		if self.tweentype==POSITION_TWEEN:
			self.rise = self.end[1]-self.start[1]
			self.run = self.end[0]-self.start[0]
			ri = self.rise
			ru = self.run
			self.elapsed += seconds
			fraction = self.elapsed/self.time

			if self.easetype==1:
				fraction = smoothstep(0,self.time,self.elapsed)

			fullru = ru*fraction
			fullri = ri*fraction
			self.sprite.rect.center = (self.start[0]+fullru,self.start[1]+fullri)
			self.current = self.sprite.rect.center
			if(self.elapsed<self.time):
				return False
			else:
				self.sprite.rect.center = self.end
				return True
		elif self.tweentype==SIZE_TWEEN:
			self.rise = self.end[1]-self.start[1]
			self.run = self.end[0]-self.start[0]
			ru = self.run
			ri = self.rise
			self.elapsed += seconds
			fraction = self.elapsed/self.time

			if self.easetype==SLIDE_EASE:
				fraction = smoothstep(0,self.time,self.elapsed)
				

			fullru = int(math.ceil(ru*fraction))
			fullri = int(math.ceil(ri*fraction))
			#self.sprite.rect.size = (self.start[0]+fullru,self.start[1]+fullri)
			self.sprite.image = pygame.transform.scale(self.sprite.image,(self.start[0]+fullru,self.start[1]+fullri))
			self.sprite.rect.size = self.sprite.image.get_size()
			self.current = self.sprite.rect.size
			if self.elapsed<self.time:
				return False
			else:
				self.sprite.image = pygame.transform.scale(self.sprite.image,(self.end[0],self.end[1]))
				self.sprite.rect.size = self.sprite.image.get_size()
				return True

		elif self.tweentype==COLOR_TWEEN:
			t1 = self.start
			r1 = t1[0]
			g1 = t1[1]
			b1 = t1[2]
			a1 = t1[3]
			t2 = self.end
			r2 = t2[0]
			g2 = t2[1]
			b2 = t2[2]
			a2 = t2[3]
			rf = r2-r1
			gf = g2-g1
			bf = b2-b1
			af = a2-a1
			self.elapsed += seconds
			fraction = self.elapsed/self.time

			if self.easetype==SLIDE_EASE:
				fraction = smoothstep(0,self.time,self.elapsed)
			
			curcolor = (r1+int(rf*fraction),g1+int(gf*fraction),b1+int(bf*fraction),a1+int(af*fraction))
			self.sprite.image.fill(curcolor)
			self.sprite.image.set_alpha(a1+int(af*fraction))
			self.sprite.color = curcolor
			if self.elapsed<self.time:
				return False
			else:
				self.sprite.image.fill(self.end)
				self.sprite.image.set_alpha(self.end[3])
				return True




class OptionCard():
	text = ""
	value = ""
	uniqueid = 0
	def __init__(self,t,v):
		self.text = t
		self.value = v
		self.uniqueid = OptionCard.uniqueid
		OptionCard.uniqueid+=1


class Card():
	name = ""
	cost = 0
	cardtype = ""
	subtype = ""
	text = ""
	hp = 0
	uniqueid = 0
	def __init__(self,n="blank",c=0,ct="blank",st="blank",t="blank",h=0):
		self.name = n
		self.cost = c
		self.cardtype = ct
		self.subtype = st
		self.text = t
		self.hp = h
		self.uniqueid = Card.uniqueid
		Card.uniqueid += 1

	def copy(self,other):
		self.name = other.name
		self.cost = other.cost
		self.cardtype = other.cardtype
		self.subtype = other.subtype
		self.text = other.text
		self.hp = other.hp
		self.uniqueid = Card.uniqueid
		Card.uniqueid += 1
		return self

class CardSprite(pygame.sprite.Sprite):
	card = None
	animating = False
	uniqueid = 0
	menuspot = (0,0)
	color = (255,255,255,255)
	display = False
	disabled = False
	colored = False
	colorspot = (0,0,0,0)
	def __init__(self,initcard,position=(0,0)):
		super(CardSprite,self).__init__()
		self.image = pygame.Surface([150,150])
		self.image.fill((255,255,255))
		self.card = initcard
		self.rect = self.image.get_rect()
		self.uniqueid = CardSprite.uniqueid
		self.menuspot = position
		self.color = (255,255,255,255)
		CardSprite.uniqueid+=1

class CardBack(pygame.sprite.Sprite):
	animating = False
	def __init__(self):
		super(CardBack,self).__init__()
		self.image = pygame.Surface([150,150])
		self.image.fill((255,255,255))
		self.rect = self.image.get_rect()


def getCard(cardid):
	return Card().copy(allcards[cardid])


initiateCardDB('coreset.xml')

card_list = pygame.sprite.Group()
top_card = pygame.sprite.Group()
zoomedcard = pygame.sprite.Group()

yourdeck = pygame.sprite.Group()

cardback = CardBack()
cardback.rect.center = (1100,650)
yourdeck.add(cardback)

drawlimbo = pygame.sprite.Group()

menu = pygame.sprite.Group()
menuhovered = pygame.sprite.Group()
menuhovered2 = pygame.sprite.Group()

tweenhelpers = []

base_stats = [10,10,10,10,10,10,10,10,10,10]
stats = [10,10,10,10,10,10,10,10,10,10]
statnames = ["Strength","Endurance","Dexterity","Speed","Intellect","Perception","Judgement","Charm","Constitution","Favor"]

updateStat = False

points_to_spend = 8

hand = [getCard(0),getCard(5),getCard(66),getCard(20),getCard(81)]
deck = [getCard(0),getCard(5),getCard(66),getCard(20),getCard(81)]
collection = []

index = 0
for card in hand:
	sprite = CardSprite(card)
	card_list.add(sprite)
	points = 750/len(hand)
	tweenhelpers.append(TweenHelper(sprite,POSITION_TWEEN,(50,(points*index)+75),0.2,SLIDE_EASE))
	index+=1

menu.add(CardSprite(OptionCard("Create a new character","new"),(600,200)))
menu.add(CardSprite(OptionCard("Load an existing character","load"),(600,500)))
tweenhelpers.append(TweenHelper(menu.sprites()[0],POSITION_TWEEN,menu.sprites()[0].menuspot,0.2,SLIDE_EASE))
tweenhelpers.append(TweenHelper(menu.sprites()[1],POSITION_TWEEN,menu.sprites()[1].menuspot,0.2,SLIDE_EASE))

opening_menu = True
ccselect = False
cckey = ""
ingame = False
flavorscreen = False

txtbx = None



#TweenHelper(cardspite1,SIZE_TWEEN,(200,200),1.0,SLIDE_EASE), TweenHelper(cardspite1,POSITION_TWEEN,(200,200),1.0,SLIDE_EASE)

_image_library = {}
def get_image(path):
	global _image_library
	image = _image_library.get(path)
	if image == None:
		canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
		image = pygame.image.load(canonicalized_path)
		_image_library[path] = image
	return image

pygame.init()

myfont = pygame.font.Font("relay-medium.ttf", 15)
smallfont = pygame.font.Font("relay-medium.ttf", 10)
costfont = pygame.font.Font("relay-medium.ttf",25)

info = ["Untitled","[race]","[class]","",""]


#pygame.mouse.set_visible(false)


screen = pygame.display.set_mode((1200, 750))
done = False

clock = pygame.time.Clock()


def drawCard(card, cardplace):
	if not cardplace==MENU_OPTION:	
		name = myfont.render(card.card.name,1,(0,0,0))
		size = myfont.size(card.card.name)
		t1 = pygame.Rect((card.rect.left+(card.rect.width/2))-(size[0]/2),card.rect.top,size[0]/2,size[1])
		screen.blit(name,t1)
		cost = costfont.render(card.card.cost,1,(0,0,0))
		size = costfont.size(card.card.cost)
		t1 = pygame.Rect(card.rect.right-size[0]-2,card.rect.top,size[0],size[1])
		screen.blit(cost,t1)
		if int(card.card.hp)!=0:
			chp = card.card.hp
			hp = costfont.render(chp,1,(0,0,0))
			size = costfont.size(chp)
			t1 = pygame.Rect(card.rect.right-2-size[0],card.rect.bottom-2-size[1],size[0],size[1])
			screen.blit(hp,t1)
	if cardplace==IN_HAND or cardplace==HAND_ZOOMED:
		randomthing = 0
	elif cardplace==ZOOMED:	
		cardtype = myfont.render(card.card.cardtype,1,(0,0,0))
		size = myfont.size(card.card.cardtype)
		subtype = smallfont.render(card.card.subtype,1,(0,0,0))
		size2 = smallfont.size(card.card.subtype)
		t1 = pygame.Rect((card.rect.left+(card.rect.width/2))-(size[0]/2),(card.rect.top+(card.rect.height/2))-(2+size2[1]),size[0],size[1])
		t2 = pygame.Rect((card.rect.left+(card.rect.width/2))-(size2[0]/2),(card.rect.top+(card.rect.height/2)),size2[0],size2[1])
		screen.blit(cardtype,t1)
		screen.blit(subtype,t2)
		linepoints = []
		incomplete = True
		start = 0
		while incomplete:
			for point in range(start,len(card.card.text)):
				substring = card.card.text[start:point]
				
				strsize = myfont.size(substring)
				if point == len(card.card.text)-1:
					linepoints.append(point+1)
					incomplete = False
					break
				if strsize[0]>card.rect.width-(card.rect.width/5):
					pit = point
					subs = card.card.text[start:pit]
					while subs[-1:]!=' ':
						pit -= 1
						subs = card.card.text[start:pit]
						#print 'pit is '+str(pit)+' and subs is '+subs
						#print 'subs[:-1] is "'+subs[:-1]+'"'
					linepoints.append(pit)
					start = linepoints[len(linepoints)-1]
					break
			
		heights = []
		widths = []
		start = 0
		for pt in linepoints:
			heights.append(myfont.size(card.card.text[start:pt])[1])
			widths.append(myfont.size(card.card.text[start:pt])[0])
			start = pt
		lines = []
		start = 0
		for pt in linepoints:
			lines.append(myfont.render(card.card.text[start:pt],1,(0,0,0)))
			start = pt
		index = 0
		offsety = 0
		for line in lines:
			if offsety-(heights[index]/2)+heights[index]+int(card.rect.height*0.63)>card.rect.height:
				theresmore = smallfont.render("[...]",1,(0,0,0))
				thesize = smallfont.size("[...]")
				therect = pygame.Rect(card.rect.left+(card.rect.width/2)-(thesize[0]/2),card.rect.bottom-(thesize[1]),thesize[0],thesize[1])
				screen.blit(theresmore,therect)
				break
			screen.blit(line,pygame.Rect((card.rect.left+(card.rect.width/2))-(widths[index]/2),((card.rect.top+(int(card.rect.height*0.63)))-(heights[index]/2))+offsety,widths[index],heights[index]))
			offsety += heights[index]*0.75
			index+=1
	elif cardplace==MENU_OPTION:
		linepoints = []
		incomplete = True
		start = 0
		while incomplete:
			for point in range(start,len(card.card.text)):
				substring = card.card.text[start:point]
				
				strsize = myfont.size(substring)
				if point == len(card.card.text)-1:
					linepoints.append(point+1)
					incomplete = False
					break
				if strsize[0]>card.rect.width-(card.rect.width/5):
					pit = point
					subs = card.card.text[start:pit]
					while subs[-1:]!=' ':
						pit -= 1
						subs = card.card.text[start:pit]
						#print 'pit is '+str(pit)+' and subs is '+subs
						#print 'subs[:-1] is "'+subs[:-1]+'"'
					linepoints.append(pit)
					start = linepoints[len(linepoints)-1]
					break
			
		heights = []
		widths = []
		start = 0
		for pt in linepoints:
			heights.append(myfont.size(card.card.text[start:pt])[1])
			widths.append(myfont.size(card.card.text[start:pt])[0])
			start = pt
		lines = []
		start = 0
		for pt in linepoints:
			lines.append(myfont.render(card.card.text[start:pt],1,(0,0,0)))
			start = pt
		index = 0
		offsety = 0
		for line in lines:
			if offsety-(heights[index]/2)+heights[index]+int(card.rect.height*0.5)>card.rect.height:
				theresmore = smallfont.render("[...]",1,(0,0,0))
				thesize = smallfont.size("[...]")
				therect = pygame.Rect(card.rect.left+(card.rect.width/2)-(thesize[0]/2),(card.rect.height/2)-(thesize[1]/2),thesize[0],thesize[1])
				screen.blit(theresmore,therect)
				break
			screen.blit(line,pygame.Rect((card.rect.left+(card.rect.width/2))-(widths[index]/2),((card.rect.top+(int(card.rect.height*0.5)))-(heights[index]/2))+offsety,widths[index],heights[index]))
			offsety += heights[index]*0.75
			index+=1

while not done:
	optionpicked = False
	events = pygame.event.get()
	for et in events:
		if et.type == pygame.QUIT:
			done = True
		if et.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			for option in menu:
				if option.rect.collidepoint(pos) and not option.disabled and not option.display:
					optionpicked = option.card.value
					print 'picked: ' + optionpicked

	pressed = pygame.key.get_pressed()

	if optionpicked:
		if opening_menu and optionpicked=="new":
			opening_menu = False
			ccselect = "initcc"
		elif flavorscreen=="main" and optionpicked=="finalize":
			flavorscreen = False
			menu.empty()
			ingame = True
		elif ccselect and optionpicked=="Races":
			ccselect = "initraces"
		elif ccselect and optionpicked=="Classes":
			ccselect = "initclasses"
		elif ccselect and optionpicked=="back":
			if ccselect == "racesmain":
				ccselect = "initcc"
			elif ccselect == "classesmain":
				ccselect = "initcc"
			elif ccselect == "ccmain":
				menu.empty()
				menu.add(CardSprite(OptionCard("Create a new character","new"),(600,200)))
				menu.add(CardSprite(OptionCard("Load an existing character","load"),(600,500)))
				tweenhelpers.append(TweenHelper(menu.sprites()[0],POSITION_TWEEN,menu.sprites()[0].menuspot,0.2,SLIDE_EASE))
				tweenhelpers.append(TweenHelper(menu.sprites()[1],POSITION_TWEEN,menu.sprites()[1].menuspot,0.2,SLIDE_EASE))
				opening_menu = True
				ccselect = False
			elif ccselect == "racecategorymain":
				ccselect="initraces"
			elif ccselect == "classcategorymain":
				ccselect="initclasses"
			elif ccselect == "statsmain":
				ccselect = "initcc"
		elif ccselect and optionpicked=="create":
			ccselect = "create"
		elif ccselect=="racesmain":
			ccselect = "initracecategory"
			cckey = optionpicked
			info[3] = cckey
		elif ccselect=="classesmain":
			ccselect = "initclasscategory"
			cckey = optionpicked
			info[4] = cckey
		elif ccselect=="racecategorymain":
			info[1] = optionpicked
			ccselect = "initcc"
		elif ccselect=="classcategorymain":
			info[2]=optionpicked
			ccselect = "initcc"
		elif ccselect=="statsmain" and optionpicked=="done":
			ccselect = False
			flavorscreen = "init"
		elif ccselect=="statsmain":
			operation = optionpicked[0]
			statid = int(optionpicked[1])
			if operation=="-":
				stats[statid]-=1
				points_to_spend+=1
			else:
				stats[statid]+=1
				points_to_spend-=1
			updateStat = statid+1

	rows = 4
	columns = 4
	acrosspoints = 1200/columns
	vertpoints = 750/rows


	if flavorscreen:
		if flavorscreen=="init":
			menu.empty()
			txtbx = eztext.Input(maxlength=13,color=(0,0,0),y=200,x=100,prompt='Name: ')
			txtbx.focus = True
			flavorscreen = "main"
			finalize = CardSprite(OptionCard("Finalize!","finalize"),(500,200))
			tweenhelpers.append(TweenHelper(finalize,POSITION_TWEEN,finalize.menuspot,0.1,SLIDE_EASE))
			menu.add(finalize)
			finalize.disabled = True
			tweenhelpers.append(TweenHelper(finalize,COLOR_TWEEN,(100,10,10,255),0.2,SLIDE_EASE))
		elif flavorscreen=="main":
			a = txtbx.update(events)
			if len(a)>0:
				menu.sprites()[0].disabled = False
			else:
				menu.sprites()[0].disabled = True



	if ccselect:
		if ccselect=="initcc":
			menu.empty()
			initiateCCDB("ccoptions.xml")
			index = 0
			for key in allcc:
				menu.add(CardSprite(OptionCard(key,key),((acrosspoints*index)+(acrosspoints/2),(vertpoints*int(index/columns))+(vertpoints/2))))
				index += 1
			menu.add(CardSprite(OptionCard("Back","back"),((acrosspoints*index)+(acrosspoints/2),(vertpoints*int(index/columns))+(vertpoints/2))))
			index+=1
			if not info[1]=="[race]" and not info[2]=="[class]":
				createbutton = CardSprite(OptionCard("Create!","create"),((acrosspoints*index)+(acrosspoints/2),(vertpoints*int(index/columns))+(vertpoints/2)))
				createbutton.colored = True
				createbutton.colorspot = (150,255,150,255)
				tweenhelpers.append(TweenHelper(createbutton,COLOR_TWEEN,(150,255,150,255),0.1,SLIDE_EASE))
				menu.add(createbutton)
			for sprite in menu:
				tweenhelpers.append(TweenHelper(sprite,POSITION_TWEEN,sprite.menuspot,0.1,SLIDE_EASE))
			ccselect="ccmain"
		elif ccselect=="initraces":
			menu.empty()
			index = 0
			for key in allcc["Races"]:
				modifier = 0
				if int(math.floor(index/columns))>0:
					modifier = -1*columns*int(math.floor(index/columns))
				menu.add(CardSprite(OptionCard(key,key),((acrosspoints*(index+modifier))+(acrosspoints/2),(vertpoints*int(math.floor(index/columns)))+(vertpoints/2))))
				index += 1
			if int(math.floor(index/columns))>0:
				modifier = -1*columns*int(math.floor(index/columns))
			menu.add(CardSprite(OptionCard("Back","back"),((acrosspoints*(index+modifier))+(acrosspoints/2),(vertpoints*int(math.floor(index/columns)))+(vertpoints/2))))
			for sprite in menu:
				tweenhelpers.append(TweenHelper(sprite,POSITION_TWEEN,sprite.menuspot,0.1,SLIDE_EASE))
			ccselect="racesmain"
		elif ccselect=="initclasses":
			menu.empty()
			index = 0
			for key in allcc["Classes"]:
				modifier = 0
				if int(math.floor(index/columns))>0:
					modifier = -1*columns*int(math.floor(index/columns))
				menu.add(CardSprite(OptionCard(key,key),((acrosspoints*(index+modifier))+(acrosspoints/2),(vertpoints*int(math.floor(index/columns)))+(vertpoints/2))))
				index += 1
			if int(math.floor(index/columns))>0:
				modifier = -1*columns*int(math.floor(index/columns))
			menu.add(CardSprite(OptionCard("Back","back"),((acrosspoints*(index+modifier))+(acrosspoints/2),(vertpoints*int(math.floor(index/columns)))+(vertpoints/2))))
			for sprite in menu:
				tweenhelpers.append(TweenHelper(sprite,POSITION_TWEEN,sprite.menuspot,0.1,SLIDE_EASE))
			ccselect="classesmain"
		elif ccselect=="initracecategory":
			menu.empty()
			index = 0
			for key in allcc["Races"][cckey]:
				modifier = 0
				if int(math.floor(index/columns))>0:
					modifier = -1*columns*int(math.floor(index/columns))
				menu.add(CardSprite(OptionCard(key,key),((acrosspoints*(index+modifier))+(acrosspoints/2),(vertpoints*int(math.floor(index/columns)))+(vertpoints/2))))
				index += 1
			if int(math.floor(index/columns))>0:
				modifier = -1*columns*int(math.floor(index/columns))
			menu.add(CardSprite(OptionCard("Back","back"),((acrosspoints*(index+modifier))+(acrosspoints/2),(vertpoints*int(math.floor(index/columns)))+(vertpoints/2))))
			for sprite in menu:
				tweenhelpers.append(TweenHelper(sprite,POSITION_TWEEN,sprite.menuspot,0.1,SLIDE_EASE))
			ccselect="racecategorymain"
		elif ccselect=="initclasscategory":
			menu.empty()
			index = 0
			for key in allcc["Classes"][cckey]:
				modifier = 0
				if int(math.floor(index/columns))>0:
					modifier = -1*columns*int(math.floor(index/columns))
				menu.add(CardSprite(OptionCard(key,key),((acrosspoints*(index+modifier))+(acrosspoints/2),(vertpoints*int(math.floor(index/columns)))+(vertpoints/2))))
				index += 1
			if int(math.floor(index/columns))>0:
				modifier = -1*columns*int(math.floor(index/columns))
			menu.add(CardSprite(OptionCard("Back","back"),((acrosspoints*(index+modifier))+(acrosspoints/2),(vertpoints*int(math.floor(index/columns)))+(vertpoints/2))))
			for sprite in menu:
				tweenhelpers.append(TweenHelper(sprite,POSITION_TWEEN,sprite.menuspot,0.1,SLIDE_EASE))
			ccselect="classcategorymain"
		elif ccselect=="create":
			menu.empty()
			for the_info in allcc["Races"][info[3]][info[1]]:
				name = the_info[0]
				amt = the_info[1]
				for iteration in range(0,int(amt)):
					collection.append(getCardByName(name))
			for the_info in allcc["Classes"][info[4]][info[2]]:
				name = the_info[0]
				amt = the_info[1]
				for iteration in range(0,int(amt)):
					collection.append(getCardByName(name))
			ccselect = "initstats"
		elif ccselect=="initstats":
			menu.empty()
			index = 0
			for i in range(0,10):
				sprite = CardSprite(OptionCard("+","+"+str(i)),(700,(i*65)+65))
				tweenhelpers.append(TweenHelper(sprite,POSITION_TWEEN,sprite.menuspot,0.1,SLIDE_EASE))
				tweenhelpers.append(TweenHelper(sprite,SIZE_TWEEN,(50,50),0.1,SLIDE_EASE))
				menu.add(sprite)
				sprite = CardSprite(OptionCard("-","-"+str(i)),(850,(i*65)+65))
				tweenhelpers.append(TweenHelper(sprite,POSITION_TWEEN,sprite.menuspot,0.1,SLIDE_EASE))
				tweenhelpers.append(TweenHelper(sprite,SIZE_TWEEN,(50,50),0.1,SLIDE_EASE))
				sprite.disabled = True
				tweenhelpers.append(TweenHelper(sprite,COLOR_TWEEN,(100,10,10,255),0.1,SLIDE_EASE))
				menu.add(sprite)
				newsprite = CardSprite(OptionCard(str(stats[i]),str(i)),(775,(i*65)+65))
				newsprite.display = True
				tweenhelpers.append(TweenHelper(newsprite,POSITION_TWEEN,newsprite.menuspot,0.1,SLIDE_EASE))
				tweenhelpers.append(TweenHelper(newsprite,SIZE_TWEEN,(50,50),0.1,SLIDE_EASE))
				menu.add(newsprite)
				newersprite = CardSprite(OptionCard(statnames[i],statnames[i]),(600,(i*65)+65))
				newersprite.display = True
				tweenhelpers.append(TweenHelper(newersprite,POSITION_TWEEN,newersprite.menuspot,0.1,SLIDE_EASE))
				tweenhelpers.append(TweenHelper(newersprite,SIZE_TWEEN,(100,50),0.1,SLIDE_EASE))
				menu.add(newersprite)
			sp = CardSprite(OptionCard("Back","back"),(1100,700))
			menu.add(sp)
			tweenhelpers.append(TweenHelper(sp,POSITION_TWEEN,sp.menuspot,0.1,SLIDE_EASE))
			lbl = CardSprite(OptionCard("Points Left: "+str(points_to_spend),"points"),(1100,300))
			lbl.display = True
			menu.add(lbl)
			tweenhelpers.append(TweenHelper(lbl,POSITION_TWEEN,lbl.menuspot,0.1,SLIDE_EASE))
			sadcumbb = CardSprite(OptionCard("Assign your stats. You may raise each stat by no more than 2, and you may not decrease any stat below 10.",""),(200,375))
			sadcumbb.display = True
			menu.add(sadcumbb)
			tweenhelpers.append(TweenHelper(sadcumbb,POSITION_TWEEN,sadcumbb.menuspot,0.1,SLIDE_EASE))
			tweenhelpers.append(TweenHelper(sadcumbb,SIZE_TWEEN,(300,200),0.1,SLIDE_EASE))
			fin = CardSprite(OptionCard("Done!","done"),(1000,650))
			fin.disabled = True
			#fin.colored = True
			#fin.colorspot = (150,255,150,255)
			menu.add(fin)
			tweenhelpers.append(TweenHelper(fin,POSITION_TWEEN,fin.menuspot,0.1,SLIDE_EASE))
			tweenhelpers.append(TweenHelper(fin,SIZE_TWEEN,(200,200),0.1,SLIDE_EASE))
			tweenhelpers.append(TweenHelper(fin,COLOR_TWEEN,(100,10,10,255),0.2,SLIDE_EASE))
			#tweenhelpers.append(TweenHelper(fin,COLOR_TWEEN,fin.colorspot,0.1,SLIDE_EASE))
			ccselect = "statsmain"


	if updateStat:
		statid = updateStat-1
		dis = False
		dos = False
		for card in menu:
			if card.card.value==str(statid):
				card.card.text = str(stats[statid])
				if stats[statid]==base_stats[statid]:
					dis = True
				if stats[statid]==base_stats[statid]+2:
					dos = True
			if card.card.value=="points":
				card.card.text = "Points Left: "+str(points_to_spend)
		for card in menu:
			if card.card.value=="-"+str(statid):
				card.disabled = dis
				if dis:	
					tweenhelpers.append(TweenHelper(card,COLOR_TWEEN,(100,10,10,255),0.2,SLIDE_EASE))
			if card.card.value=="+"+str(statid):
				card.disabled = dos
				if dos:
					tweenhelpers.append(TweenHelper(card,COLOR_TWEEN,(100,10,10,255),0.2,SLIDE_EASE))


		if points_to_spend==0:
			for card in menu:
				if not card.card.value=="":
					if card.card.value[0]=="+":
						card.disabled = True
						tweenhelpers.append(TweenHelper(card,COLOR_TWEEN,(100,10,10,255),0.2,SLIDE_EASE))
					elif card.card.value=="done":
						card.disabled = False
						card.colorspot = (150,255,150,255)
						card.colored = True

		else:
			for card in menu:
				if not card.card.value=="":
					if card.card.value[0]=="+":
						if not stats[int(card.card.value[1])]==base_stats[int(card.card.value[1])]+2:
							card.disabled = False
					elif card.card.value=="done":
						card.disabled = True
						tweenhelpers.append(TweenHelper(card,COLOR_TWEEN,(100,10,10,255),0.2,SLIDE_EASE))
						card.colored = False
		updateStat = False


	if pressed[pygame.K_SPACE] and bool(zoomedcard) and not zoomedcard.sprites()[0].animating:
		points = 750/len(hand)
		ind = hand.index(zoomedcard.sprites()[0].card)
		tweenhelpers.append(TweenHelper(zoomedcard.sprites()[0],POSITION_TWEEN,(50,(points*ind)+75),0.3,SLIDE_EASE))
		tweenhelpers.append(TweenHelper(zoomedcard.sprites()[0],SIZE_TWEEN,(150,150),0.3,SLIDE_EASE))
		card_list.add(zoomedcard.sprites()[0])
		zoomedcard.empty()
	elif pressed[pygame.K_SPACE] and bool(top_card) and top_card.sprites()[0].rect.collidepoint(pygame.mouse.get_pos()) and not top_card.sprites()[0].animating:
		tweenhelpers.append(TweenHelper(top_card.sprites()[0],POSITION_TWEEN,(600,375),0.3,SLIDE_EASE))
		tweenhelpers.append(TweenHelper(top_card.sprites()[0],SIZE_TWEEN,(350,350),0.3,SLIDE_EASE))
		zoomedcard.add(top_card.sprites()[0])
		top_card.empty()
	elif pressed[pygame.K_d] and yourdeck.sprites()[0].rect.collidepoint(pygame.mouse.get_pos()) and not bool(drawlimbo) and not bool(zoomedcard):
		cardtodraw = deck.pop(0)
		hand.append(cardtodraw)
		points = 750/len(hand)
		ind = hand.index(cardtodraw)
		sprite = CardSprite(cardtodraw)
		sprite.image = pygame.transform.scale(sprite.image,(1,1))
		sprite.rect = sprite.image.get_rect()
		sprite.rect.center = yourdeck.sprites()[0].rect.center
		drawlimbo.add(sprite)
		tweenhelpers.append(TweenHelper(sprite,SIZE_TWEEN,(150,150),0.3,SLIDE_EASE))
		tweenhelpers.append(TweenHelper(sprite,POSITION_TWEEN,(50,(points*ind)+75),0.3,SLIDE_EASE))
		index = 0
		for card in card_list:	
			tweenhelpers.append(TweenHelper(card,POSITION_TWEEN,(50,(points*hand.index(card.card))+75),0.3,SLIDE_EASE))
			index+=1

	for card in card_list:
			if card.rect.collidepoint(pygame.mouse.get_pos()) and not card.animating and not bool(top_card):
				tweenhelpers.append(TweenHelper(card,SIZE_TWEEN,(200,200),0.1,SLIDE_EASE))
				card_list.remove(card)
				top_card.add(card)

	if bool(top_card) and not top_card.sprites()[0].rect.collidepoint(pygame.mouse.get_pos()) and not top_card.sprites()[0].animating:
		tweenhelpers.append(TweenHelper(top_card.sprites()[0],SIZE_TWEEN,(150,150),0.1,SLIDE_EASE))
		card_list.add(top_card.sprites()[0])
		top_card.empty()

	for card in menu:
		if (opening_menu or ccselect or flavorscreen) and card.rect.collidepoint(pygame.mouse.get_pos()) and not card.disabled and not card.display and not card.animating and not pygame.mouse.get_pressed()[0]:
			bigsize = 300
			if ccselect=="statsmain":
				bigsize=100
				if card.card.value=="done":
					bigsize=200
			tweenhelpers.append(TweenHelper(card,SIZE_TWEEN,(bigsize,bigsize),0.1,SLIDE_EASE))
			tweenhelpers.append(TweenHelper(card,POSITION_TWEEN,card.menuspot,0.1,SLIDE_EASE))
			tweenhelpers.append(TweenHelper(card,COLOR_TWEEN,(255,255,100,255),0.1,SLIDE_EASE))
			menuhovered2.add(card)
		elif (opening_menu or ccselect or flavorscreen) and (not card.display and not card.animating and not card.rect.collidepoint(pygame.mouse.get_pos())) or (not card.animating and card.disabled):
			normsize = 150
			if ccselect=="statsmain":
				normsize=50
				if card.card.value=="done":
					normsize=100
			tweenhelpers.append(TweenHelper(card,SIZE_TWEEN,(normsize,normsize),0.1,SLIDE_EASE))
			tweenhelpers.append(TweenHelper(card,POSITION_TWEEN,card.menuspot,0.1,SLIDE_EASE))
			if not card.disabled and not card.colored:
				tweenhelpers.append(TweenHelper(card,COLOR_TWEEN,(255,255,255,255),0.1,SLIDE_EASE))
			elif not card.disabled and card.colored:
				tweenhelpers.append(TweenHelper(card,COLOR_TWEEN,card.colorspot,0.1,SLIDE_EASE))
			elif card.disabled:
				tweenhelpers.append(TweenHelper(card,COLOR_TWEEN,(100,10,10,255),0.2,SLIDE_EASE))
			menuhovered.empty()
			menuhovered2.empty()

	for tween in tweenhelpers:
		step = 1/FRAMERATE
		#print step
		if tween.step(step):
			tween.sprite.animating = False
			tweenhelpers.remove(tween)
			if drawlimbo.has(tween.sprite):
				card_list.add(tween.sprite)
				drawlimbo.remove(tween.sprite)
		else:
			tween.sprite.animating = True

	


	screen.fill((100,100,100))
	

	if ccselect:
		show = myfont.render(info[0]+", the "+info[1]+" "+info[2],1,(0,0,0))
		sizey = myfont.size(info[0]+", the "+info[1]+" "+info[2])
		recty = pygame.Rect(600-(sizey[0]/2),730-sizey[1],sizey[0],sizey[1])
		background = pygame.Surface((recty.width,recty.height))
		background.fill((255,255,255))
		screen.blit(background,recty)
		screen.blit(show,recty)
		menuhovered.draw(screen)
		menu.draw(screen)
		for card in menu:
			drawCard(card,MENU_OPTION)

	if opening_menu:
		menuhovered.draw(screen)
		menu.draw(screen)
		for card in menu:
			drawCard(card,MENU_OPTION)
		
	if flavorscreen:
		txtbx.draw(screen)
		menu.draw(screen)
		for card in menu:
			drawCard(card,MENU_OPTION)

	if ingame:	
		yourdeck.draw(screen)
		thdeck = myfont.render("Your Deck: "+str(len(deck))+" cards",1,(0,0,0))
		thsize = myfont.size("Your Deck: "+str(len(deck))+" cards")
		recto = pygame.Rect(yourdeck.sprites()[0].rect.left+(yourdeck.sprites()[0].rect.width/2)-(thsize[0]/2),yourdeck.sprites()[0].rect.top+(yourdeck.sprites()[0].rect.height/2)-thsize[1],thsize[0],thsize[1])
		screen.blit(thdeck,recto)

		card_list.draw(screen)



		for card in card_list:
			drawCard(card,IN_HAND)
				
		top_card.draw(screen)

		if bool(top_card):
			drawCard(top_card.sprites()[0],HAND_ZOOMED)

		zoomedcard.draw(screen)

		if bool(zoomedcard):
			drawCard(zoomedcard.sprites()[0],ZOOMED)

		drawlimbo.draw(screen)
		if bool(drawlimbo):
			drawCard(drawlimbo.sprites()[0],IN_HAND)

	pygame.display.flip()
	clock.tick(FRAMERATE)