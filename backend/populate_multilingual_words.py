#!/usr/bin/env python3
"""
Comprehensive script to populate word-of-day data for multiple languages
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models import create_tables
from db_service import db_service
import json

# Comprehensive word data for multiple languages
MULTILINGUAL_WORDS = {
    'en': [
        {
            'word': 'hello',
            'translation': 'a greeting or expression of goodwill',
            'pronunciation': 'həˈloʊ',
            'part_of_speech': 'interjection',
            'difficulty': 'beginner',
            'example_sentence': 'Hello, how are you today?',
            'example_translation': 'A common greeting used when meeting someone.',
            'etymology': 'From Old English hæl (whole, healthy)',
            'related_words': ['hi', 'greetings', 'salutation'],
            'cultural_note': 'The most common greeting in English-speaking countries.'
        },
        {
            'word': 'serendipity',
            'translation': 'the occurrence of events by chance in a happy way',
            'pronunciation': 'ˌser.ənˈdɪp.ə.ti',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'It was pure serendipity that we met at the coffee shop.',
            'example_translation': 'Describes pleasant surprises or fortunate accidents.',
            'etymology': 'Coined by Horace Walpole in 1754 from the Persian fairy tale',
            'related_words': ['chance', 'fortune', 'luck', 'coincidence'],
            'cultural_note': 'A beloved English word expressing life\'s pleasant surprises.'
        },
        {
            'word': 'wanderlust',
            'translation': 'a strong desire to travel and explore the world',
            'pronunciation': 'ˈwɒn.də.lʌst',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Her wanderlust led her to visit 30 countries.',
            'example_translation': 'Used to describe someone with a passion for traveling.',
            'etymology': 'From German wandern (to hike) + lust (desire)',
            'related_words': ['travel', 'adventure', 'exploration'],
            'cultural_note': 'Reflects the human desire for exploration and discovery.'
        },
        {
            'word': 'mellifluous',
            'translation': 'having a sweet, smooth, pleasing sound',
            'pronunciation': 'məˈlɪf.lu.əs',
            'part_of_speech': 'adjective',
            'difficulty': 'advanced',
            'example_sentence': 'Her mellifluous voice captivated the audience.',
            'example_translation': 'Describes something that sounds beautiful and flowing.',
            'etymology': 'From Latin mel (honey) + fluere (to flow)',
            'related_words': ['melodious', 'harmonious', 'sweet-sounding'],
            'cultural_note': 'Often used to describe beautiful singing or speaking voices.'
        },
        {
            'word': 'resilience',
            'translation': 'the ability to recover quickly from difficulties',
            'pronunciation': 'rɪˈzɪl.i.əns',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'She showed remarkable resilience after the setback.',
            'example_translation': 'The capacity to bounce back from challenges.',
            'etymology': 'From Latin resilire (to rebound)',
            'related_words': ['strength', 'toughness', 'adaptability'],
            'cultural_note': 'Highly valued quality in personal and professional contexts.'
        }
    ],
    'es': [
        {
            'word': 'sobremesa',
            'translation': 'time spent at the table after finishing a meal',
            'pronunciation': 'so.βɾeˈme.sa',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'La sobremesa duró más que la cena.',
            'example_translation': 'The after-dinner conversation lasted longer than dinner.',
            'etymology': 'From sobre (over) + mesa (table)',
            'related_words': ['charla', 'conversación', 'tertulia'],
            'cultural_note': 'An important social custom in Spanish-speaking countries.'
        },
        {
            'word': 'duende',
            'translation': 'a quality of passion and inspiration, especially in flamenco',
            'pronunciation': 'ˈdwen.de',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'El bailaor de flamenco tiene mucho duende.',
            'example_translation': 'The flamenco dancer has great spirit and charm.',
            'etymology': 'From dueño (owner), originally meaning a magical creature',
            'related_words': ['alma', 'espíritu', 'pasión'],
            'cultural_note': 'Essential concept in flamenco and Spanish arts.'
        },
        {
            'word': 'madrugada',
            'translation': 'dawn, early morning hours',
            'pronunciation': 'ma.ðɾuˈɣa.ða',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Me despierto en la madrugada para estudiar.',
            'example_translation': 'I wake up in the early morning to study.',
            'etymology': 'From madrugar (to get up early)',
            'related_words': ['amanecer', 'alba', 'aurora'],
            'cultural_note': 'Often associated with peaceful, quiet moments.'
        },
        {
            'word': 'estrenar',
            'translation': 'to use or wear something for the first time',
            'pronunciation': 'es.tɾeˈnaɾ',
            'part_of_speech': 'verb',
            'difficulty': 'intermediate',
            'example_sentence': 'Voy a estrenar mis zapatos nuevos.',
            'example_translation': 'I\'m going to wear my new shoes for the first time.',
            'etymology': 'From estreno (premiere, debut)',
            'related_words': ['debut', 'primera vez', 'inaugurar'],
            'cultural_note': 'Often used for clothing, movies, or new experiences.'
        },
        {
            'word': 'querencia',
            'translation': 'a place where one feels safe and at home',
            'pronunciation': 'ke.ˈɾen.θja',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Este café es mi querencia en la ciudad.',
            'example_translation': 'This café is my safe haven in the city.',
            'etymology': 'From querer (to love, to want)',
            'related_words': ['hogar', 'refugio', 'santuario'],
            'cultural_note': 'Deeply rooted in Spanish culture and bullfighting tradition.'
        }
    ],
    'fr': [
        {
            'word': 'dépaysement',
            'translation': 'the feeling of being in a foreign place',
            'pronunciation': 'de.pɛ.iz.mɑ̃',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Le dépaysement total lors de mon premier voyage à Tokyo.',
            'example_translation': 'The complete feeling of displacement during my first trip to Tokyo.',
            'etymology': 'From dé- (un-) + pays (country)',
            'related_words': ['voyage', 'étranger', 'expatriation'],
            'cultural_note': 'Unique French concept with no direct English equivalent.'
        },
        {
            'word': 'flâner',
            'translation': 'to wander aimlessly with pleasure',
            'pronunciation': 'flɑ.ne',
            'part_of_speech': 'verb',
            'difficulty': 'intermediate',
            'example_sentence': 'J\'aime flâner dans les rues de Paris.',
            'example_translation': 'I love strolling through the streets of Paris.',
            'etymology': 'From Old Norse flana (to rush about)',
            'related_words': ['se promener', 'errer', 'déambuler'],
            'cultural_note': 'Central to Parisian culture and the art of leisurely observation.'
        },
        {
            'word': 'retrouvailles',
            'translation': 'the joy of reuniting with someone after a long separation',
            'pronunciation': 'ʁə.tʁu.vaj',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Nos retrouvailles après dix ans étaient émouvantes.',
            'example_translation': 'Our reunion after ten years was moving.',
            'etymology': 'From retrouver (to find again)',
            'related_words': ['réunion', 'rencontre', 'revoir'],
            'cultural_note': 'Captures the special emotion of reuniting with loved ones.'
        },
        {
            'word': 'savoir-vivre',
            'translation': 'knowledge of how to live well and behave properly',
            'pronunciation': 'sa.vwaʁ.vivʁ',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Son savoir-vivre impressionne toujours les invités.',
            'example_translation': 'His good manners always impress the guests.',
            'etymology': 'From savoir (to know) + vivre (to live)',
            'related_words': ['étiquette', 'politesse', 'bonnes manières'],
            'cultural_note': 'Essential concept in French social interactions.'
        },
        {
            'word': 'l\'esprit d\'escalier',
            'translation': 'thinking of the perfect reply too late',
            'pronunciation': 'lɛs.pʁi des.ka.lje',
            'part_of_speech': 'noun phrase',
            'difficulty': 'advanced',
            'example_sentence': 'J\'ai eu l\'esprit d\'escalier après notre débat.',
            'example_translation': 'I thought of the perfect comeback after our debate.',
            'etymology': 'Literally "staircase wit" - wit that comes when leaving',
            'related_words': ['regret', 'répartie', 'après-coup'],
            'cultural_note': 'Coined by French philosopher Denis Diderot.'
        }
    ],
    'de': [
        {
            'word': 'Fernweh',
            'translation': 'longing for distant places; wanderlust',
            'pronunciation': 'ˈfɛʁn.veː',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Sie hat Fernweh nach den Bergen.',
            'example_translation': 'She longs for the mountains.',
            'etymology': 'From fern (far) + Weh (pain)',
            'related_words': ['Heimweh', 'Reisefieber', 'Wanderlust'],
            'cultural_note': 'Reflects German romantic ideals of travel and exploration.'
        },
        {
            'word': 'Gemütlichkeit',
            'translation': 'warmth, coziness, and good cheer',
            'pronunciation': 'ɡəˈmyːt.lɪç.kaɪt',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Die Gemütlichkeit des Cafés lädt zum Verweilen ein.',
            'example_translation': 'The coziness of the café invites you to linger.',
            'etymology': 'From Gemüt (mind, spirit) + -lich (like) + -keit (-ness)',
            'related_words': ['Behaglichkeit', 'Wärme', 'Geborgenheit'],
            'cultural_note': 'Central to German culture and hospitality.'
        },
        {
            'word': 'Verschlimmbessern',
            'translation': 'to make something worse by trying to improve it',
            'pronunciation': 'fɛɐ̯ˈʃlɪm.bɛ.sɐn',
            'part_of_speech': 'verb',
            'difficulty': 'advanced',
            'example_sentence': 'Er hat das Problem nur verschlimmbessert.',
            'example_translation': 'He only made the problem worse by trying to fix it.',
            'etymology': 'From verschlimmern (to worsen) + verbessern (to improve)',
            'related_words': ['verschlechtern', 'vermurksen', 'verpfuschen'],
            'cultural_note': 'Captures the irony of well-intentioned but counterproductive actions.'
        },
        {
            'word': 'Waldeinsamkeit',
            'translation': 'the feeling of solitude in the forest',
            'pronunciation': 'ˈvalt.aɪn.zaːm.kaɪt',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Die Waldeinsamkeit half ihm beim Nachdenken.',
            'example_translation': 'The forest solitude helped him think.',
            'etymology': 'From Wald (forest) + Einsamkeit (solitude)',
            'related_words': ['Einsamkeit', 'Ruhe', 'Besinnung'],
            'cultural_note': 'Reflects German romanticism and connection to nature.'
        },
        {
            'word': 'Zeitgeist',
            'translation': 'the spirit or mood of a particular time period',
            'pronunciation': 'ˈtsaɪt.ɡaɪst',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Der Zeitgeist der 60er Jahre war revolutionär.',
            'example_translation': 'The spirit of the 60s was revolutionary.',
            'etymology': 'From Zeit (time) + Geist (spirit)',
            'related_words': ['Epoche', 'Ära', 'Stimmung'],
            'cultural_note': 'Widely adopted into English and other languages.'
        }
    ],
    'ja': [
        {
            'word': '木漏れ日',
            'translation': 'sunlight filtering through trees',
            'pronunciation': 'ko-mo-re-bi',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': '木漏れ日が森の中で踊っている。',
            'example_translation': 'Sunlight is dancing through the trees in the forest.',
            'etymology': 'From 木 (tree) + 漏れ (leak) + 日 (sun)',
            'related_words': ['日光', '森林', '陽射し'],
            'cultural_note': 'Reflects Japanese appreciation for subtle natural beauty.'
        },
        {
            'word': '侘寂',
            'translation': 'finding beauty in imperfection and impermanence',
            'pronunciation': 'wa-bi-sa-bi',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': '古い茶碗に侘寂の美しさを感じる。',
            'example_translation': 'I feel the beauty of wabi-sabi in the old tea bowl.',
            'etymology': 'From 侘 (loneliness) + 寂 (tranquility)',
            'related_words': ['美', '不完全', '無常'],
            'cultural_note': 'Central aesthetic philosophy in Japanese art and culture.'
        },
        {
            'word': 'もったいない',
            'translation': 'regret over waste; too good to waste',
            'pronunciation': 'mot-tai-nai',
            'part_of_speech': 'adjective',
            'difficulty': 'intermediate',
            'example_sentence': 'まだ食べられるのに捨てるなんてもったいない。',
            'example_translation': 'It\'s wasteful to throw it away when it\'s still edible.',
            'etymology': 'From Buddhist concept of intrinsic value',
            'related_words': ['無駄', '惜しい', '節約'],
            'cultural_note': 'Reflects Japanese values of conservation and respect for resources.'
        },
        {
            'word': '森林浴',
            'translation': 'forest bathing; therapeutic time in nature',
            'pronunciation': 'shin-rin-yo-ku',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': '週末は森林浴でリラックスしています。',
            'example_translation': 'I relax with forest bathing on weekends.',
            'etymology': 'From 森林 (forest) + 浴 (bathing)',
            'related_words': ['自然', '癒し', 'リラックス'],
            'cultural_note': 'Japanese practice now recognized worldwide for health benefits.'
        },
        {
            'word': '一期一会',
            'translation': 'once in a lifetime encounter; treasure the moment',
            'pronunciation': 'i-chi-go-i-chi-e',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': '今日の出会いは一期一会ですね。',
            'example_translation': 'Today\'s meeting is a once-in-a-lifetime encounter.',
            'etymology': 'From tea ceremony philosophy',
            'related_words': ['出会い', '瞬間', '大切'],
            'cultural_note': 'Important concept in Japanese tea ceremony and relationships.'
        }
    ],
    'zh': [
        {
            'word': '缘分',
            'translation': 'predestined relationship or connection',
            'pronunciation': 'yuán-fèn',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': '我们能相遇真是缘分。',
            'example_translation': 'Our meeting is truly fate.',
            'etymology': 'From 缘 (connection) + 分 (portion)',
            'related_words': ['命运', '缘份', '注定'],
            'cultural_note': 'Important concept in Chinese philosophy and relationships.'
        },
        {
            'word': '孝顺',
            'translation': 'filial piety; respect and care for parents',
            'pronunciation': 'xiào-shùn',
            'part_of_speech': 'adjective/noun',
            'difficulty': 'intermediate',
            'example_sentence': '他是个很孝顺的儿子。',
            'example_translation': 'He is a very filial son.',
            'etymology': 'From 孝 (filial piety) + 顺 (obedience)',
            'related_words': ['尊敬', '孝心', '侍奉'],
            'cultural_note': 'Fundamental virtue in Confucian culture.'
        },
        {
            'word': '面子',
            'translation': 'face; dignity and reputation in social contexts',
            'pronunciation': 'miàn-zi',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': '给他留点面子吧。',
            'example_translation': 'Let\'s save some face for him.',
            'etymology': 'From 面 (face) + 子 (suffix)',
            'related_words': ['尊严', '脸面', '声誉'],
            'cultural_note': 'Crucial concept in Chinese social interactions.'
        },
        {
            'word': '风水',
            'translation': 'feng shui; harmonious arrangement of environment',
            'pronunciation': 'fēng-shuǐ',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': '这个房子的风水很好。',
            'example_translation': 'This house has good feng shui.',
            'etymology': 'From 风 (wind) + 水 (water)',
            'related_words': ['和谐', '环境', '平衡'],
            'cultural_note': 'Ancient Chinese practice of spatial arrangement.'
        },
        {
            'word': '道',
            'translation': 'the Way; path of natural order and harmony',
            'pronunciation': 'dào',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': '他在寻找人生的道。',
            'example_translation': 'He is seeking the Way of life.',
            'etymology': 'Ancient Chinese philosophical concept',
            'related_words': ['路', '方法', '哲学'],
            'cultural_note': 'Central concept in Taoism and Chinese philosophy.'
        }
    ],
    'it': [
        {
            'word': 'sprezzatura',
            'translation': 'studied carelessness; effortless grace',
            'pronunciation': 'spret.tsa.ˈtu.ra',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'La sua sprezzatura nel vestire è ammirevole.',
            'example_translation': 'His effortless elegance in dressing is admirable.',
            'etymology': 'From sprezzare (to despise, to scorn)',
            'related_words': ['eleganza', 'grazia', 'naturalezza'],
            'cultural_note': 'Renaissance ideal of appearing naturally graceful.'
        },
        {
            'word': 'dolce far niente',
            'translation': 'the sweetness of doing nothing',
            'pronunciation': 'ˈdol.tʃe far ˈnjen.te',
            'part_of_speech': 'phrase',
            'difficulty': 'intermediate',
            'example_sentence': 'Oggi ho voglia di dolce far niente.',
            'example_translation': 'Today I feel like enjoying the sweetness of doing nothing.',
            'etymology': 'From dolce (sweet) + far (to do) + niente (nothing)',
            'related_words': ['riposo', 'relax', 'ozio'],
            'cultural_note': 'Italian appreciation for leisure and contemplation.'
        },
        {
            'word': 'passeggiata',
            'translation': 'evening stroll for socializing',
            'pronunciation': 'pas.sed.ˈdʒa.ta',
            'part_of_speech': 'noun',
            'difficulty': 'beginner',
            'example_sentence': 'Facciamo una passeggiata in centro?',
            'example_translation': 'Shall we take a stroll in the city center?',
            'etymology': 'From passeggiare (to walk, to stroll)',
            'related_words': ['camminata', 'giro', 'passeggiate'],
            'cultural_note': 'Important Italian social tradition, especially in small towns.'
        },
        {
            'word': 'abbiocco',
            'translation': 'drowsiness after a big meal',
            'pronunciation': 'ab.ˈbjok.ko',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Dopo il pranzo della nonna, ho sempre l\'abbiocco.',
            'example_translation': 'After grandma\'s lunch, I always get drowsy.',
            'etymology': 'Roman dialect, possibly from abbiocare',
            'related_words': ['sonnolenza', 'torpore', 'digestione'],
            'cultural_note': 'Common experience after traditional Italian meals.'
        },
        {
            'word': 'struggimento',
            'translation': 'intense longing or yearning',
            'pronunciation': 'strud.dʒi.ˈmen.to',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Prova uno struggimento per la sua terra natale.',
            'example_translation': 'He feels an intense longing for his homeland.',
            'etymology': 'From struggere (to melt, to consume)',
            'related_words': ['nostalgia', 'desiderio', 'malinconia'],
            'cultural_note': 'Deep emotional concept often found in Italian poetry.'
        }
    ],
    'pt': [
        {
            'word': 'saudade',
            'translation': 'deep nostalgic longing for something absent',
            'pronunciation': 'saw.ˈda.dʒi',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Tenho saudade dos tempos de escola.',
            'example_translation': 'I have nostalgia for school days.',
            'etymology': 'From Latin solitas (solitude)',
            'related_words': ['nostalgia', 'longing', 'melancolia'],
            'cultural_note': 'Quintessential Portuguese emotion, untranslatable to other languages.'
        },
        {
            'word': 'desenrascanço',
            'translation': 'the art of finding creative solutions to problems',
            'pronunciation': 'de.zen.ʁas.ˈkɐ̃.su',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'O desenrascanço português é famoso no mundo todo.',
            'example_translation': 'Portuguese resourcefulness is famous worldwide.',
            'etymology': 'From desenrascar (to get out of trouble)',
            'related_words': ['criatividade', 'jeitinho', 'improviso'],
            'cultural_note': 'Reflects Portuguese resourcefulness and problem-solving spirit.'
        },
        {
            'word': 'cafuné',
            'translation': 'gently running fingers through someone\'s hair',
            'pronunciation': 'ka.fu.ˈnɛ',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Ela fazia cafuné no filho para ele dormir.',
            'example_translation': 'She gently stroked her son\'s hair to help him sleep.',
            'etymology': 'From African languages brought to Brazil',
            'related_words': ['carinho', 'caricia', 'mimo'],
            'cultural_note': 'Tender gesture common in Brazilian family relationships.'
        },
        {
            'word': 'madrugada',
            'translation': 'early morning hours before dawn',
            'pronunciation': 'ma.dɾu.ˈɡa.da',
            'part_of_speech': 'noun',
            'difficulty': 'beginner',
            'example_sentence': 'Acordo sempre na madrugada para estudar.',
            'example_translation': 'I always wake up in the early morning to study.',
            'etymology': 'From madrugar (to rise early)',
            'related_words': ['aurora', 'alvorecer', 'amanhecer'],
            'cultural_note': 'Often associated with quiet, peaceful moments.'
        },
        {
            'word': 'gambiarra',
            'translation': 'makeshift solution using improvised materials',
            'pronunciation': 'gɐ̃.bi.ˈa.ʁa',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Fez uma gambiarra para consertar a televisão.',
            'example_translation': 'He made a makeshift fix for the television.',
            'etymology': 'From theater lighting equipment',
            'related_words': ['improviso', 'jeitinho', 'adaptação'],
            'cultural_note': 'Represents Brazilian ingenuity and resourcefulness.'
        }
    ],
    'ru': [
        {
            'word': 'тоска',
            'translation': 'deep spiritual anguish or melancholy',
            'pronunciation': 'tos.ka',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Его охватила тоска по родине.',
            'example_translation': 'He was overcome with longing for his homeland.',
            'etymology': 'Old Slavic root meaning to yearn',
            'related_words': ['грусть', 'печаль', 'меланхолия'],
            'cultural_note': 'Central emotion in Russian literature and soul.'
        },
        {
            'word': 'авось',
            'translation': 'perhaps; hope that things will work out somehow',
            'pronunciation': 'a.vosʲ',
            'part_of_speech': 'adverb',
            'difficulty': 'intermediate',
            'example_sentence': 'Авось всё получится.',
            'example_translation': 'Maybe everything will work out.',
            'etymology': 'From "а вось" (and what if)',
            'related_words': ['может быть', 'возможно', 'надежда'],
            'cultural_note': 'Reflects Russian optimism despite uncertainty.'
        },
        {
            'word': 'душа',
            'translation': 'soul; deep inner spiritual essence',
            'pronunciation': 'du.ʂa',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'У неё красивая душа.',
            'example_translation': 'She has a beautiful soul.',
            'etymology': 'Proto-Slavic duša',
            'related_words': ['дух', 'сердце', 'внутренний мир'],
            'cultural_note': 'Fundamental concept in Russian spirituality and character.'
        },
        {
            'word': 'удаль',
            'translation': 'brave daring; spirited courage',
            'pronunciation': 'u.dalʲ',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'Молодецкая удаль покорила всех.',
            'example_translation': 'His spirited courage won everyone over.',
            'etymology': 'From удалый (daring, brave)',
            'related_words': ['смелость', 'отвага', 'храбрость'],
            'cultural_note': 'Traditional Russian ideal of bold, spirited bravery.'
        },
        {
            'word': 'широта',
            'translation': 'breadth; generosity of spirit',
            'pronunciation': 'ʂɨ.ro.ta',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'Широта русской души известна всем.',
            'example_translation': 'The breadth of the Russian soul is known to all.',
            'etymology': 'From широкий (wide, broad)',
            'related_words': ['щедрость', 'великодушие', 'размах'],
            'cultural_note': 'Associated with the Russian concept of generous, expansive character.'
        }
    ],
    'ar': [
        {
            'word': 'طرب',
            'translation': 'musical ecstasy; deep emotional response to music',
            'pronunciation': 'ta.rab',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'أصابه الطرب من سماع الأغنية.',
            'example_translation': 'He was moved to ecstasy by hearing the song.',
            'etymology': 'Classical Arabic root ط-ر-ب',
            'related_words': ['موسيقى', 'انفعال', 'وجد'],
            'cultural_note': 'Central concept in Arabic musical tradition.'
        },
        {
            'word': 'كرم',
            'translation': 'hospitality; generous treatment of guests',
            'pronunciation': 'ka.ram',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'اشتهر بكرمه وحسن ضيافته.',
            'example_translation': 'He was famous for his generosity and hospitality.',
            'etymology': 'From root ك-ر-م meaning nobility',
            'related_words': ['ضيافة', 'سخاء', 'جود'],
            'cultural_note': 'Fundamental virtue in Arab culture and tradition.'
        },
        {
            'word': 'صبر',
            'translation': 'patience; endurance in face of hardship',
            'pronunciation': 'sabr',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'الصبر مفتاح الفرج.',
            'example_translation': 'Patience is the key to relief.',
            'etymology': 'From root ص-ب-ر',
            'related_words': ['تحمل', 'احتمال', 'مثابرة'],
            'cultural_note': 'Highly valued virtue in Islamic culture and philosophy.'
        },
        {
            'word': 'حنين',
            'translation': 'nostalgia; yearning for the past',
            'pronunciation': 'ha.nin',
            'part_of_speech': 'noun',
            'difficulty': 'intermediate',
            'example_sentence': 'يشعر بحنين إلى أيام الطفولة.',
            'example_translation': 'He feels nostalgia for childhood days.',
            'etymology': 'From root ح-ن-ن meaning to long for',
            'related_words': ['شوق', 'اشتياق', 'ذكرى'],
            'cultural_note': 'Common theme in Arabic poetry and literature.'
        },
        {
            'word': 'وجد',
            'translation': 'spiritual ecstasy; intense mystical experience',
            'pronunciation': 'wajd',
            'part_of_speech': 'noun',
            'difficulty': 'advanced',
            'example_sentence': 'دخل في حالة وجد أثناء الذكر.',
            'example_translation': 'He entered a state of spiritual ecstasy during remembrance.',
            'etymology': 'From root و-ج-د meaning to find',
            'related_words': ['انتشاء', 'حال', 'وله'],
            'cultural_note': 'Important concept in Islamic mysticism and Sufism.'
        }
    ]
}

def populate_all_languages():
    """Populate word-of-day data for all languages"""
    print("🌍 Populating multilingual word-of-day database...")
    print("=" * 60)
    
    # Ensure database tables exist
    create_tables()
    
    total_added = 0
    total_failed = 0
    
    for language, words in MULTILINGUAL_WORDS.items():
        print(f"\n📚 Processing {language.upper()} ({len(words)} words)...")
        added_count = 0
        failed_count = 0
        
        for word_data in words:
            success = db_service.add_word_of_day(language, word_data)
            if success:
                added_count += 1
                total_added += 1
                print(f"  ✅ Added: {word_data['word']}")
            else:
                failed_count += 1
                total_failed += 1
                print(f"  ❌ Failed: {word_data['word']}")
        
        print(f"  📊 {language.upper()}: {added_count} added, {failed_count} failed")
        
        # Verify by getting a random word
        test_word = db_service.get_word_of_day(language)
        if test_word:
            print(f"  🔍 Verification: Found '{test_word['word']}'")
        else:
            print(f"  ⚠️  Verification failed for {language}")
    
    print("\n" + "=" * 60)
    print(f"🎉 COMPLETION SUMMARY:")
    print(f"   📊 Total words added: {total_added}")
    print(f"   ❌ Total failures: {total_failed}")
    print(f"   🌐 Languages processed: {len(MULTILINGUAL_WORDS)}")
    print(f"   ✨ Available languages: {', '.join(MULTILINGUAL_WORDS.keys())}")
    
    return total_added, total_failed

def test_random_words():
    """Test by getting random words from each language"""
    print("\n🎲 Testing random word retrieval...")
    print("-" * 40)
    
    for language in MULTILINGUAL_WORDS.keys():
        word_data = db_service.get_word_of_day(language)
        if word_data:
            print(f"🇺🇳 {language.upper()}: {word_data['word']} - {word_data['translation'][:50]}...")
        else:
            print(f"❌ {language.upper()}: No words found")

if __name__ == "__main__":
    try:
        added, failed = populate_all_languages()
        test_random_words()
        
        if added > 0:
            print(f"\n🎊 SUCCESS! Added {added} words across {len(MULTILINGUAL_WORDS)} languages!")
        else:
            print(f"\n💔 FAILED! No words were added to the database.")
            
    except Exception as e:
        print(f"\n💥 ERROR: {e}")
        import traceback
        traceback.print_exc() 