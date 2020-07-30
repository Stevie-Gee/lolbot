# coding=utf-8

""" Original concept and execution by Vendetta"""

from __future__ import unicode_literals

import random
import bot_utils

QUESTIONS = [
"Would you rather: Lose the ability to speak? Or lose the ability to read?",
"Would you rather: Have one Get Out of Jail free card? Or a key that can unlock any door?",
"Would you rather: Live on a sailboat? Or live in an RV?",
"Would you rather: Have an easy job working for someone else? Or be self employed and work incredibly hard?",
"Would you rather: Create a cure for a deadly disease? Or be the first person to explore a new planet?",
"Would you rather: Be king of a huge country 2500 years ago? Or be an average person in todays society?",
"Would you rather: Be forced to dance to every song you heard? Or be forced to sing along to every song you heard?",
"Would you rather: Travel the world on a very tight budget? Or live in a 3rd World Country for a year in luxury?",
"Would you rather: Suddenly be elected a Senator with absolutely no knowledge on how to be a Senator? Or suddenly become a CEO for a large company with absolutely no knowledge on how to be a CEO?",
"Would you rather: Drink Strawberry milk for life? Or regukar milk everyday for 5 years",
"Would you rather: Live in the real world but not be able to talk to anyone or interact with anything? Or live in Virtual Reality where you have the power to do anything?",
"Would you rather: Live until you're 100 but look 100 years old the whole time? Or die at 45 while looking like a 25 year old?",
"Would you rather: Watch the whole series of X Files? Or watch the whole series of My Little Pony?",
"Would you rather: Your only mode of transport be an Cheetah with saftey features like a seat belt? Or the Flinstones Bedrock car with absolutely no saftety features like brakes?",
"Would you rather: Play would you rathers all day? Or sit on your bed thinking about masturbating to pass the time but can't get it up all day?",
"Would you rather: Find out how much wood a Woodchuck actually chucks? Or kill that spider that scared Little Ms Muffet?",
"Would you rather: Moderate a sports game? Or actually play the sport yourself",
"Would you rather: Read erotica? Or watch it?",
"Would you rather: Mistakingly send nudes to your mother? Or your boss?",
"Would you rather: Be kinky? Or be romantic?",
"Would you rather: Do it with your cousin? Or be the one to end the relationship with your true love?",
"Would you rather: Grant everyone's sexual wishes? Or have yours granted but have everyone know your deepest darkest kinks?",
"Would you rather: Have loved and lost? Or to never have loved at all",
"Would you rather: Be buried alive? Or burn to death?",
"Would you rather: Have no phone afer 9pm? Or have your parents monitor your computer traffic?",
"Would you rather: Listen to old hip hop for life? Or listen to rap your whole life?",
"Would you rather: Win cash? Or give cash to someone in need?",
"Would you rather: Live a poor life with the one you love? Or be rich and all alone?",
"Would you rather: Find true everlasting love? Or cure cancer?",
"Would you rather: Spend the last momnets of your life with your family? Or doing something crzy you've always wanted to do?",
"Would you rather: Except the ugly truth? Or live a life based on lies?",
"Would you rather: Be stuck on the moon? Or float freely in space?",
"Would you rather: Tell everyone your guilty pleasures? Or never partake in your guilty pleasures ever again?",
"Would you rather: Know everything and die tomorrow? Or live forever but be ignorant",
"Would you rather: Dance like MJ? Or sing like Freddy Mercury?",
"Would you rather: Be a dog person in a world of cats? Or vice versa? ",
"Would you rather: Be famous but have your fame spoiled by a controversy? Or become a hero in the military but everyone dies in your squad and no one can tell your story",
"Would you rather: Die rich and successful? Or die happy?",
"Would you rather: Live without Facebook? Or YouTube?",
"Would you rather: Live without Twitter or Instagram?",
"Would you rather: Live the life of an entrepreneur with all the stresses? Or be stuck in one job with decent pay?",
"Would you rather: Go on a reality survival show and lose? Or go on a reality dating show and get rejected?",
"Would you rather: Sing a song in front of strangers? Or in front of friends?",
"Would you rather: Tell your crush you like them? Or tell someone you're not interested in that you don't like them back?",
"Would you rather: Tell everyone your darkest fears? Or tell people your darkest secrets?",
"Would you rather: Eat black liquorise everyday for the rest of your life? Or have suicidal thoughts?",
#I guess these are the majority of the dirty ones...
"Would you rather: Have an obsessive girlfriend / boyfriend? Or a hot, cheating one?",
"Would you rather: Make love in a Jacuzzi? Or on the beach?",
"Would you rather: Walk in on your parents making love? Or have them walk in on you?",
"Would you rather: Be a kinky kind of person? Or be the romantic kind of person?",
"Would you rather: Have sex with 3 hot girls, Or have sex with your crush?",
"Would you rather: Sleep with your cousin and have no one know about it? Or not sleep with your cousin and have everyone think you did?",
"Would you rather: Be poor and have sex? Or be rich and never have sex?",
"Would you rather: Let your partner sleep with YOUR best friend? Or let your partner sleep with THEIR bst friend?",
"Would you rather: Give a lap dance? Or a strip tease?",
"Would you rather: Cuddle in front of the fireplace? Or set fire to your bed?",
"Would you rather: Make a sex tape with the person of your dreams and have them catch you? Or have your crush make a sex tape with you and you never find out?",
"Would you rather: Watch an romantic anime alone? Or watch a heartbreaking anime with your crush?",
"Would you rather: Lose the sense of feeling while making love? Or lose the ability to taste?",
"Would you rather: Get caressed by a girl? Or caress her?",
#Damn it I'm still not done
"Would you rather: Eat vegetables like a normal human being? Or live off chocolate for the next 10 years",
"Would you rather: Be emotionless? Or feel too much?",
"Would you rather: Play Would You Rather? Or Never Have I Ever?",
"Would you rather: Play Would You Rather? Or grillme?",
"Would you rather: Have Apple products? Or Samsung products?",
"Would you rather: Vomit through your nose? Or poop through your mouth?  ( ͡° ͜ʖ ͡°)",
"( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°) You chose the lenny card. Pick again ( ͡° ͜ʖ ͡°) ( ͡° ͜ʖ ͡°)",
"Would you rather: Keep playing? Or Stop?",
"Would you rather: Lolbot get banned for saying the unholy vagina word? Or just lose the ability to play with him ever again?",
"By the power invested in me, I now pronounce you and Vendetta husband and... Oh right this is would you rather... Try again please!",
"Would you rather: Be born a guy with a girlish voice? Or be born a girl with a guy voice?",
"Would you rather: Super glue your peepee shut? Or your anus?",
# Just the throw aways for "comedic effect"
"Hold on my butt itches.. Try again.",
"If you're reading this, then congratulations! That means you can try again!",
"Did you know Daddy Longleg spiders are technically not spiders since they have a penis? With that said - Would you rather be a Daddy Longleg? Or a normal anthropod?",
"Donkey Kong was named Donkey because the creator thought 'Donkey' meant 'dumb' in English for 'Dumb Ape'. With that said - Would you rather live in the world of Mario? Or the world of Donkey Kong?",
"How Vendetta feels after coding the Would You Rather command: https://i.pinimg.com/236x/47/61/8a/47618a67ac32c8b687624d764bb3e8b0--programming-memes.jpg",
#Okay back to the questions
#77 above
"Would you rather: Live the greatest day of your life then die? Or live forever?",
"Would you rather: Give up Breakfast? Lunch? Or Dinner?",
"Would you rather: Be a famous actor / actress? or be a famous director?",
"Would you rather: Be a deep sea diver? Or an Astronaut?",
"Would you rather: Take a 100% guaranteed $100,000? Or take a 50/50 chance at $1,000,000?",
]

# Walk backwards through the QUESTIONS list so we don't repeat a question.
# Once we fall off the front of the index, shuffle the list and start again.
Q_INDEX = -1

@bot_utils.command("wyr")
def call(msg):
    """Ask the heathen a Would You Rather question"""
    
    # "Vendetta is awesome he's so totally sexy too"
    # - Vendetta
    
    global Q_INDEX
    
    if Q_INDEX < 0:
        random.shuffle(QUESTIONS)
        Q_INDEX = len(QUESTIONS)
    
    Q_INDEX -= 1
    reply = "<@%s>: %s" % (msg["d"]["author"]["id"], QUESTIONS[Q_INDEX])
    bot_utils.reply(msg, reply)
