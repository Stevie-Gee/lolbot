"""Summons a random loli. Because my friends are perverts."""

import random
import bot_utils

SUMMON = [
    'brings forth a',
    'summons up a',
    'unlocks the basement door and frees a',
    'opens his van and lets out a',
    'goes to the graveyard and digs up a fresh',
    'bends over and pulls from out his ass a',
    'gives birth to a',
    'is dead... Here\'s a',
    'pulls from out the freezer a',
    'goes to the orphanage and brings you back a',
    'rubs one out on your chest, and it turns out to be a',
    'rocks out with his cock out... Here\'s a',
    'rips open his stomach and pulls out a',
    'sexually assaults you, but apologizes by giving you a',
    'shits on your chest, but the shit turns out to actually be a',
    'goes downtown and buys you a',
    'reaches down into your pants and rubs your ass until you fart out a mystical cloud which slowly materializes into a',
    'lactates out a',
    'introduces you to a',
    'steals from AmericanIdiot\'s basement a',
    'has his way with your ass, and then pays you with a',
    'pulls from out of his belly button a',
    'goes to the betting stations and wins you a',
    'kidnaps for you a',
    'spat his baby juices into Twilight, and now gives to you their child, a',
    'steals one of your ribs and turns it into a',
    'cuts his wrist and out comes a',
    'sets off on an adventure and can\'t summon for you at the moment, but while he\'s gone, here\'s a',
    'has a sex change, and becomes a',
    'sneezes out a',
    'drives a limo up and gets out to open the door for a',
    'orders a present for you from eBay, containing a',
    'fires from out a cannon a',
    'fucked your mom and made a',
    'cums in your face... here\'s a',
    'gives you a computer virus while distracting you with a',
    'uses some old popsicle sticks, two rubber bands, and some cyanide to create a',
    'uses sugar, spice, and everything nice to create a',
    'travels throughout the universe to find you the best',
    'tries to ignore you, but realize you won\'t leave him alone, so to shut you up, he gives you a',
    'drags in a screaming and kicking',
    'reaches into the future and grabs you a',
    'rips open your chest and pulls out a',
    'has a hard time, but manages to piss out a',
    'confesses that he is God, and uses his magical powers to give you a',
    'reaches up into your ass, and pulls out a',
    'throws a Poke\'ball which releases a',
    'teaches you the importance of sexual education by giving you a',
    'blows up an orphanage, leaving nothing but this',
    'announces that you\'re the winner of this',
    'just doesn\'t give a shit... Here\'s a',
    'googles you a',
    'steals your money, but makes up for it by giving you a',
    'dives into hell and brings you back a',
    'pulls from out of Santa\'s sack',
    'barfs up a',
    'opens a can of',
    'sends an email to you, containing a',
    'makes you a cardboard cutout of a',
    'goes to the Farmers\' Market and purchases you a',
    'builds you a cybernetic',
    'sends you off to a secluded island with nothing but a',
    'is having a dream about you and a',
    'carefully injects you with a',
    'pretends to be a',
    'opens his torrenting software, and pirates you a',
    'slices and dices at unsuspecting victims, and then stitches them together to make you a',
    'uses his ties with the illuminati to get you a',
    'chants something or another while waving his wand at a baked potato, which suddenly transforms into a',
    'uses Hitler\'s DNA to create a',
    'provides you with enough drugs to believe you have a',
    'opens Pandora\'s box, and pulls out a',
    'uses black magic and a dash of paprika to summon you a',
    'pulls up in his white van and exchanges your money for his newly obtained',
    'beats you with a baseball bat... As consolation, have this',
    'uses his magic and turns your mother into a',
    'uses his dick-cheese to sculpt you a',
    'placed a blind-fold on you and guided you into the bedroom. Once the blind-fold was lifted, you found yourself standing in front of a',
    'squeezes your ass cheeks while licking your neck... Have this',
    ]

EYETYPE = [
    'dark',
    'sparkling',
    'bright',
    'clear',
    'creepy',
    'dreamy',
    'lustful',
    'phantom',
    'beautiful',
    'seductive',
    ]

EYECOLOUR = [
    'green',
    'blue',
    'brown',
    'red',
    'silver',
    'purple',
    'heterochromic',
    'ocean blue',
    'blood red',
    ]

HAIRSTYLE = [
    'curly',
    'straight',
    'pigtailed',
    'braided',
    'kinky',
    'frizzy',
    'wavy',
    'long',
    'short',
    ]

HAIRCOLOUR = [
    'dark brown',
    'brown',
    'light blond',
    'blond',
    'jet black',
    'black',
    'dark green',
    'green',
    'bright red',
    'red',
    'dark red',
    'light blue',
    'dark blue',
    'shiny and silver',
    'purple',
    'dark purple',
    'blood stained',
    'bright pink',
    'glowing gold',
    ]

CLOTHES = [
    'wearing nothing but a t-shirt.',
    'wearing a school uniform.',
    'wearing a clown costume.',
    'dressed in a soft red robe.',
    'dressed in a shimmering mist.',
    'dressed like a princess.',
    'dressed like a pirate.',
    'in a body bag.',
    'dressed as a sailor.',
    'naked and drenched in honey.',
    'dressed in her girl scouts uniform.',
    'coated in chocolate.',
    'wearing a military uniform.',
    'wearing your skin.',
    'dressed as a Pokemon trainer.',
    'dressed in a Hitler costume.',
    'a cybernetic zombie from the future!',
    'wearing a Pikachu costume.',
    'dressed like a biker.',
    'costumed as the Pedo Bear.',
    'wearing a mecha exosuit.',
    'strapped in leather.',
    'wearing ducky print pajamas.',
    'wearing a mini skirt and a short top.',
    'dressed like Rebecca Black.',
    'disguised as Jenni.',
    'costumed as a furry,',
    'wearing her baseball uniform.',
    'wearing nothing but a nightgown.',
    'wearing nothing but a bikini.',
    'wearing a yellow sundress.',
    'wearing nothing but an apron.',
    'dressed in gothic attire.',
    'wearing a ducky costume.',
    'completely naked.',
    'costumed as a super hero!',
    'wearing a nun outfit.',
    'costumed as a nekomimi.',
    'wearing a ninja costume.',
    'dressed like a boy.',
    'wearing her soccer uniform.',
    'wearing a Lost_Rose costume.',
    'wearing a Twilight costume.',
    'dressed in a suit and tie.',
    'wrapped in a bow.',
    'dressed like a ballerina.',
    'dressed for Sunday school.',
    'wearing nothing but socks.',
    'soaked in the blood of the innocent.',
    'wearing cute pink undies.',
    'wearing nothing but a kimono.',
    'dressed like a whore.',
    'wearing your father\'s foreskin stretched around her head, as a headband.',
    'draped in the flesh of your family.',
    'cosplaying as Harley Quinn.',
    'wearing a suit made out of dirty diapers...',
    'completely over-dressed for this occasion.',
    'wearing nothing. Not even flesh.',
    'covered in bees!',
    'wearing a Tanooki Suit.',
    'wearing only a t-shirt and those striped stockings that you love so much.',
    'butt-naked and dripping in chocolate.',
    'cosplaying as that anime chick you like.',
    'cosplaying as that female videogame character that you like.',
    'cosplaying as Hannibal Lecter.',
    'strapped in bombs.',
    'secretly a trap.',
    'naked and ready for her bath.',
    'dressed to impress.',
    'coated in pubes from your uncle.',
    'wearing the same thing as you! This is embarrassing...',
    'coated in cotton candy.',
    ]

AFTERMATH = [
    'touches you inappropriately.',
    'climbs on your head and lays an egg.',
    'puts a gun in your hand and holds it against her head.',
    'has sex with you while recording it, and then reports the video to the police.',
    'takes off her clothes and masturbates in front of you.',
    'eats the last cookie!',
    'grabs you by the head and tapes your face to the receiving end of a glory hole, and then invites all your friends.',
    'caresses your face and makes out with you.',
    'aggressively has her way with you!',
    'sneaks up and hugs you tightly from behind.',
    'pouts up at you with tears forming in her eyes.',
    'slices your face off and serves it to your family.',
    'reminds you of the game, which you just lost!',
    'sends you a YouTube link http://www.youtube.com/watch?v=oHg5SJYRHA0',
    'wishes you had a dick that could actually satisfy her.',
    'sits down besides you and leans against your leg.',
    'approaches and playfully tugs at your pants.',
    'asks you for a spanking, and declares that she has been rather naughty.',
    'goes back to SIG, because SIG is better than you.',
    'shits in the floor and makes you clean it.',
    'spreads her legs wide, and invites you in.',
    'steals your computer and browses 4chan.',
    'shyly approaches and tries to get you to help with her math homework.',
    'goes to the kitchen to make you a sammich.',
    'forces your clothes off and molests you!',
    'violently give you oral!',
    'rips your spine out and uses it to masturbate!',
    'gets on her hands and knees, hikes her butt up, and barks at you.',
    'smashes your face against her crotch and begins to piss!',
    'doesn\'t waste any time, and proceeds to oil up.',
    'smashes your face against her ass and begins to shit!',
    'exposes that she has a penis, and isn\'t a she at all!',
    'warns you that she isn\'t cheap.',
    'grabs a knife and stabs you uncontrollably!',
    'wraps her arms around you, and tells you to never let go.',
    'took the midnight train going anywhere.',
    'steals your wallet and rides off into the night on a goat.',
    'gets down on her knees in front of you, spreads your legs wide open, and begins to toss your salad.',
    'gets down on her knees in front of you, spreads your legs wide open, and shouts "FALCON PUNCH" before punching your crotch!',
    'approaches slowly, and gives you special permission to touch her where ever you want.',
    'mashes your potatoes, if you know what I mean...',
    'climbs a tree and flashes her ass at you, and suggests you\'ll never get it.',
    'suggests that you summon another girl, cause she\'s not interested.',
    'tells you that you\'re ugly, and that you don\'t deserve her.',
    'shyly approaches and kisses your cheek.',
    'shyly approaches and puts her hand in your pants.',
    'gives all your friends oral, and then kisses you.',
    'begins to mumble in some strange language and places a curse on you. You have three days left to live!',
    'shits in a box and gift wraps it for you.',
    'digs a hole in the backyard and tells you to get in.',
    'tells you that your father was right, and that you\'ll never amount to anything!',
    'gets lubed up and has sex with everyone in the room, except you.',
    'points and laughs at your penis!',
    'turns into a vampire, and sinks her teeth into your neck!',
    'turns out to be a cyborg from the future, and she has come back in time to end your life!',
    'turns out to be a zombie, and begins to bite you!',
    'has unprotected sex with you, and then reveals that she has herpes.',
    'smiles up to you from inside the bathtub, right before dropping the toaster in!',
    'begs you to eat her out before midnight, or else she\'ll turn to dust!',
    'puts a finger up your butt and whispers that you\'re gonna be her bitch!',
    'seductively approaches and bends over for you.',
    'climbs into your arms and begs to be fucked!',
    'grabs a baseball bat and mashes your crotch with it!',
    'grabs multiple golf balls and begins to place them in your ass.',
    'eats all your candy and then leaves.',
    'seductively gives your crotch a massage.',
    'steals all your candy and hides it in her pussy.',
    'wraps herself around your leg, and begins to hump it.',
    'shyly approaches and smiles up to you.',
    'downs a bottle of vodka and grins up at you.',
    'engages you in a PokeBattle to determine if you\'re strong enough to take her virginity. She chooses to use her Geodude!',
    'explodes...',
    'sits in your lap and plays video games.',
    'rubs soap all over herself and then gives you a full contact bath, using her body.',
    'gives you a free lap dance.',
    'mashes her crotch against your face and demands satisfaction!',
    'brings a donkey into the room, and puts on a show that you\'ll never forget!',
    'ties you up and puts a blindfold on you before bringing her father in to have his way with you.',
    'straps on a dildo and begins to rape you!',
    'rips a hole in the time space continuum!',
    'hands you a gun, and tells you to be at the bank by noon.',
    'leans over a table and spreads her butt cheeks for you.',
    'rubs her naughty places before kneeling down to unzip your pants.',
    'quickly darts towards you and kicks you in the nuts!',
    'walks up, shyly holding out a flower for you.',
    'shyly approaches and licks your cheek.',
    'rings your doorbell and then runs away.',
    'rings your doorbell and then excitedly shouts "Trick or Treat!"',
    'becomes drunk with lust and demands satisfaction!',
    'looks up at you, puckering her lips for a kiss.',
    'sits down beside you and asks you to brush her hair.',
    'angelically smiles at you, and begins pelting you with tiny pickles.',
    'climbs into your bed and pretends to fall asleep.',
    'climbs into bed and asks you for a bedtime story.',
    'yawns, and snuggles sleepily against your chest.',
    'suddenly rips her arm off and beats you to death with it.',
    'twirls her hair and poses a little for you.',
    'farts out a rainbow, and then throws candy sprinkles in your eyes.',
    'runs towards you to have a good time, with a nice dime bag in her hand!',
    'gives you what could have been a great handjob, if she hadn\'t used hotsauce.',
    'spits your dad\'s cum into your mouth!',
    'pokes at your naughty places while wearing a seductive grin!',
    'beats you to death with a fetus!',
    '360 no-scopes you, and then fucks your mom!',
    'provides reasonable services, in exchange for money.',
    'gently bites your dick off.',
    'rubs your ass with itching powder!',
    'uses your dick as a straw, and sucks away at your youth!',
    'gathers all her little friends and runs a train on you.',
    'puts her dick in your mouth?',
    'sexually assaults your grandmother!',
    'tells you that you\'re too old for her, and that you should date someone your own age.',
    'never really existed, but it\'s the thought that counts.',
    'turns out to be your mother, from the past! Do you wish to continue?',
    'exposes her tender body, and asks you to be gentle.',
    'climbs up and into your ass, and then proceeds to make herself at home.',
    'has daddy issues.',
    'proudly queefs the alphabet!',
    'bends over and exposes her ass, just before spreading her cheeks and releasing hundreds of spiders from her rectum!',
    ]

def call(msg):
    """Summon a random loli for you."""
    content = msg.get("d").get("content")
    if ' ' in content:
        thing = content.split(None, 1)[1]
    else:
        thing = "loli"
    
    age = "%s year old" % random.randint(5, 15)
    text = "_%s %s %s, with %s %s eyes, %s %s hair, and is %s She %s_" % (
        random.choice(SUMMON),
        age,
        thing,
        random.choice(EYETYPE),
        random.choice(EYECOLOUR),
        random.choice(HAIRSTYLE),
        random.choice(HAIRCOLOUR),
        random.choice(CLOTHES),
        random.choice(AFTERMATH),
        )
    bot_utils.reply(msg, text)

HELP = """Summons a friend for you to play with."""

COMMANDS = {
    "summon": call,
}
