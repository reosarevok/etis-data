import datetime, requests
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
def submit_date(date, property, sources):
    claim = pywikibot.Claim(repo, property)
    claim.setTarget(date)
    item.addClaim(claim,
                  summary=u'Importing dates from the Estonian Research Portal')
    claim.addSources(sources,
                     summary=u'Importing dates from the Estonian Research Portal')


site = pywikibot.Site("wikidata", "wikidata")
repo = site.data_repository()

statedin = pywikibot.Claim(repo, "P248")
erp = pywikibot.ItemPage(repo, "Q11824870")
statedin.setTarget(erp)
refdate = pywikibot.Claim(repo, "P813")
today = datetime.datetime.today()
date = pywikibot.WbTime(year=today.year, month=today.month, day=today.day)
refdate.setTarget(date)

# We get all items that have an etis.ee ID
query = "SELECT ?item WHERE { ?item wdt:P2953 [] }"
generator = pg.WikidataSPARQLPageGenerator(query, site=site)

for item in generator:
    # We get the Wikidata item
    item.get()
    print(item.id)
    # There should only ever exist one ID per item, so we take the first
    personID = item.claims[u'P2953'][0].target
    # The new "IDs" are names, so we need to remove the underscores to query
    print(personID)
    # We look at the etis.ee page to get the date of birth and the date of death if present
    response = requests.get(
        "https://www.etis.ee:7443/api/cvest/getitems?Format=json&SearchType=1&Take=1&Skip=0&PersonId=" + personID)
    data = response.json()
    if len(data) > 0:
        person = data[0]
        birthDate = person['DateOfBirth']
        deathDate = person['DateOfDeath']
        etisIDRef = pywikibot.Claim(repo, "P2953")
        etisIDRef.setTarget(personID)
        # We turn the dates into something Wikidata can recognize
        birthWikiDate = None
        if birthDate != "":
            birthWikiDate = date_to_wikidate(birthDate)

        deathWikiDate = None
        if deathDate != "":
            deathWikiDate = date_to_wikidate(deathDate)

        # If there's a date and WD doesn't have a date yet, we send it
        if birthWikiDate is None:
            print("No birth date")
        elif not (u'P569' in item.claims):
            submit_date(birthWikiDate, "P569", [statedin, etisIDRef, refdate])
            print("Sending birth date " + birthDate)
        else:
            statedin = pywikibot.Claim(repo, "P248")
            erp = pywikibot.ItemPage(repo, "Q11824870")
            statedin.setTarget(erp)
            for claim in item.claims[u'P569']:
                has_etis_source = False
                for source in claim.sources:
                    if u'P248' in source:
                        for source_target in source[u'P248']:
                            if source_target.target == erp:
                                has_etis_source = True

                if claim.target != birthWikiDate:
                    print("Date clash for " + item.getID())
                elif has_etis_source == False:
                    claim.addSources([statedin, etisIDRef, refdate],
                                     summary=u'Importing dates from the Estonian Research Portal')
                    print("Adding reference to existing date " + deathDate)
                else:
                    print("Date already present with ETIS reference")


        if deathWikiDate is None:
            print("No death date")
        elif not (u'P570' in item.claims):
            submit_date(deathWikiDate, "P570", [statedin, etisIDRef, refdate])
            print("Sending death date " + deathDate)
        else:
            for claim in item.claims[u'P570']:
                has_etis_source = False
                has_full_etis_source = False
                for source in claim.sources:
                    if u'P248' in source:
                        for source_target in source[u'P248']:
                            if source_target.target == erp:
                                has_etis_source = True

                if claim.target != deathWikiDate:
                    print("Date clash for " + item.getID())
                elif has_etis_source == False:
                    claim.addSources([statedin, etisIDRef, refdate],
                                     summary=u'Importing dates from the Estonian Research Portal')
                    print("Adding reference to existing date " + deathDate)
                else:
                    print("Date already present with ETIS reference")
    else:
        print ("No data found")
