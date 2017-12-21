import urllib, json
import pywikibot
from pywikibot import pagegenerators as pg


# Turns a date into something Wikidata can recognize
def date_to_wikidate(date):
    tempDate = date.split('.')
    day = int(tempDate[0])
    month = int(tempDate[1])
    year = int(tempDate[2])
    return pywikibot.WbTime(year=year, month=month, day=day)


# Sends a date to Wikidata
def submit_date(date, property):
    claim = pywikibot.Claim(repo, property)
    claim.setTarget(date)
    item.addClaim(claim,
                  summary=u'Importing dates from the Estonian Research Portal')
    statedin = pywikibot.Claim(repo, "P248")
    erp = pywikibot.ItemPage(repo, "Q11824870")
    statedin.setTarget(erp)
    claim.addSources([statedin],
                     summary=u'Importing dates from the Estonian Research Portal')


site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()

# We get all items that have an etis.ee ID
query = "SELECT ?item WHERE { ?item wdt:P2953 [] . MINUS { ?item wdt:P569 [] } } LIMIT 50"
generator = pg.WikidataSPARQLPageGenerator(query, site=site)

for item in generator:
    # We get the Wikidata item
    item.get()
    # There should only ever exist one ID per item, so we take the first
    personID = item.claims[u'P2953'][0].target
    print personID

    # We look at the etis.ee page to get the date of birth and the date of death if present
    response = urllib.urlopen(
        "https://www.etis.ee:7443/api/cvest/getitems?Format=json&SearchType=1&Take=1&Skip=0&PersonId=" + personID)
    data = json.loads(response.read())
    person = data[0]
    birthDate = person['DateOfBirth']
    print birthDate
    deathDate = person['DateOfDeath']
    print deathDate

    # We turn the dates into something Wikidata can recognize
    birthWikiDate = None
    if birthDate != "":
        birthWikiDate = date_to_wikidate(birthDate)
        print birthWikiDate

    deathWikiDate = None
    if deathDate != "":
        deathWikiDate = date_to_wikidate(deathDate)
        print deathWikiDate

    # If there's a date and WD doesn't have a date yet, we send it
    if birthWikiDate is not None and not (u'P569' in item.claims):
        submit_date(birthWikiDate, "P569")
        print "Birth date!"
    else:
        print "No birth date"

    if deathWikiDate is not None and not (u'P570' in item.claims):
        submit_date(deathWikiDate, "P570")
        print "Death date!"
    else:
        print "No death date"
