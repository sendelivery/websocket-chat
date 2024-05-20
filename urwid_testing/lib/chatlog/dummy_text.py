from typing import Generator


dummy_text = [
    "Hello all, how are you all doing?",
    "This is great, a real life chat application!",
    "It's so cool how we can all talk together in the same room!",
    "The tumbleweed refused to tumble but was more than willing to prance.",
    "The hummingbird's wings blurred while it eagerly sipped the sugar water from the feeder.",
    "His son quipped that power bars were nothing more than adult candy bars.",
    "The fog was so dense even a laser decided it wasn't worth the effort.",
    "They throw cabbage that turns your brain into emotional baggage.",
    "I never knew what hardship looked like until it started raining bowling balls.",
    "The crowd yells and screams for more memes.",
    "He hated that he loved what she hated about hate.",
    "She hadn't had her cup of coffee, and that made things all the worse.",
    "I can't believe this is the eighth time I'm smashing open my piggy bank on the same day!",
    "My uncle's favorite pastime was building cars out of noodles.",
    "Nancy was proud that she ran a tight shipwreck.",
    "The random sentence generator generated a random sentence about a random sentence.",
    "His thought process was on so many levels that he gave himself a phobia of heights.",
    "Edith could decide if she should paint her teeth or brush her nails.",
    "Improve your goldfish's physical fitness by getting him a bicycle.",
    "The swirled lollipop had issues with the pop rock candy.",
    "I'm a great listener, really good with empathy vs sympathy and all that, but I hate people.",
    "Hit me with your pet shark!",
    "The virus had powers none of us knew existed.",
]


def generate_dummy_text() -> Generator[str, None, None]:
    for text in dummy_text:
        yield text
