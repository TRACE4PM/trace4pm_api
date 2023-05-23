
def update_logs(logs, collection_db):
    for i, log in enumerate(logs):
        sessions = log['sessions']
        client_id = log['client_id']
        for j, session in enumerate(sessions):
            requests = apply_tagging(session['requests'])
            save_to_db(client_id, j, requests)
    return True


def apply_tagging(requests):
    for i, request in enumerate(requests):
        request = request['request_url']
        pos1 = request.find('ark')
        pos2 = request.find('sru')
        pos3 = request.find('search')
        pos4 = request.find('und')
        pos5 = request.find('/accueil/')
        pos6 = request.find('AdvancedSearch')
        pos7 = request.find('blog')
        pos8 = request.find('statistic')
        pos9 = request.find('detail')
        pos10 = request.find('snippet')
        pos11 = request.find('status')
        ### navigation page d'acceuil gallica###
        if ('und' in request and '/accueil/' in request):
            if (pos4 > pos5):  # acceuil before und
                request = '##HomePage'+request
                requests[i]['request_tag'] = 'HomePage'
            elif (pos5 > pos4):
                request = '##CollectionNavigation'+request
                requests[i]['request_tag'] = 'CollectionNavigation'
        elif ('blog' in request and '/accueil/' in request):
            if (pos7 > pos5):  # acceuil before blog
                request = '##HomePage'+request
                requests[i]['request_tag'] = 'HomePage'
            elif (pos5 > pos7):
                request = '##AccessGallicaBlog'+request
                requests[i]['request_tag'] = 'AccessGallicaBlog'
        elif ('AdvancedSearch' in request and '/accueil/' in request):
            if (pos6 > pos5):  # acceuil before AdvancedSearch
                request = '##HomePage'+request
                requests[i]['request_tag'] = 'HomePage'
            elif (pos5 > pos6):
                request = '##AdvancedSearch'+request
                requests[i]['request_tag'] = 'AdvancedSearch'
        elif ('sru' in request and '/accueil/' in request):
            if (pos2 > pos5):  # acceuil before sru
                request = '##HomePage'+request
                requests[i]['request_tag'] = 'HomePage'
            elif (pos5 > pos2):
                request = '##GallicaSearchEngine'+request
                requests[i]['request_tag'] = 'GallicaSearchEngine'
        elif ('search' in request and '/accueil/' in request):
            if (pos3 > pos5):  # acceuil before search
                request = '##HomePage'+request
                requests[i]['request_tag'] = 'HomePage'
            elif (pos5 > pos3):
                request = '##GallicaSearchEngine'+request
                requests[i]['request_tag'] = 'GallicaSearchEngine'
        elif ('ark' in request and '/accueil/' in request):
            if (pos1 > pos5):  # acceuil before ark
                request = '##HomePage'+request
                requests[i]['request_tag'] = 'HomePage'
            elif (pos5 > pos1):
                request = '##ViewingRessource'+request
                requests[i]['request_tag'] = 'ViewingRessource'
        elif ('/accueil/' in request):
            request = '##HomePage'+request
            requests[i]['request_tag'] = 'HomePage'
        #### télécharger une ressource###
        elif ('download' in request):
            request = '##DownloadRessource'+request
            requests[i]['request_tag'] = 'DownloadRessource'
        ### extraction des rapports de recherche gallica###
        elif ('ark' in request and 'statistic' in request):
            if (pos1 > pos8):  # acceuil before ark
                request = '##ResearchReportExtraction'+request
                requests[i]['request_tag'] = 'ResearchReportExtraction'
            elif (pos8 > pos1):
                request = '##ViewingRessource'+request
                requests[i]['request_tag'] = 'ViewingRessource'
        elif ('ark' in request and 'detail' in request):
            if (pos1 > pos9):  # acceuil before ark
                request = '##ResearchReportExtraction'+request
                requests[i]['request_tag'] = 'ResearchReportExtraction'
            elif (pos9 > pos1):
                request = '##ViewingRessource'+request
                requests[i]['request_tag'] = 'ViewingRessource'
        elif ('ark' in request and 'snippet' in request):
            if (pos1 > pos10):  # acceuil before ark
                request = '##ResearchReportExtraction'+request
                requests[i]['request_tag'] = 'ResearchReportExtraction'
            elif (pos10 > pos1):
                request = '##ViewingRessource'+request
                requests[i]['request_tag'] = 'ViewingRessource'
        elif ('ark' in request and 'status' in request):
            if (pos1 > pos11):  # acceuil before ark
                request = '##ResearchReportExtraction'+request
                requests[i]['request_tag'] = 'ResearchReportExtraction'
            elif (pos11 > pos1):
                request = '##ViewingRessource'+request
                requests[i]['request_tag'] = 'ViewingRessource'
        elif ('statistic' in request or 'detail' in request or 'snippet' in request or
              'status' in request):
            request = '##ResearchReportExtraction'+request
            requests[i]['request_tag'] = 'ResearchReportExtraction'
        ### accès ressource gallica###
        elif ('ark' in request and 'sru' in request):
            if (pos2 > pos1):
                request = '##ViewingRessource'+request
                requests[i]['request_tag'] = 'ViewingRessource'
            elif (pos1 > pos2):
                request = '##GallicaSearchEngine'+request
                requests[i]['request_tag'] = 'GallicaSearchEngine'
        elif ('ark' in request and 'texteImage' in request):
            request = '##OCRTextExtraction'+request
            requests[i]['request_tag'] = 'OCRTextExtraction'
        elif ('ark' in request and 'search' in request):
            if (pos3 > pos1):
                request = '##ViewingRessource'+request
                requests[i]['request_tag'] = 'ViewingRessource'
            elif (pos1 > pos3):
                request = '##GallicaSearchEngine'+request
                requests[i]['request_tag'] = 'GallicaSearchEngine'
        elif ('ark' in request):
            request = '##ViewingRessource'+request
            requests[i]['request_tag'] = 'ViewingRessource'
        elif ('RequestDigitalElement' in request):
            request = '##ViewingRessource'+request
            requests[i]['request_tag'] = 'ViewingRessource'
        elif ('dossiers' in request):
            request = '##ViewingRessource'+request
            requests[i]['request_tag'] = 'ViewingRessource'
        ### recherce avancée gallica###
        elif ('advancedSearch' in request and 'search' in request):
            request = '##AdvancedSearch'+request
            requests[i]['request_tag'] = 'AdvancedSearch'
        elif ('advanced' in request and 'search' in request):
            request = '##AdvancedSearch'+request
            requests[i]['request_tag'] = 'AdvancedSearch'
        ### utilisation du moteur de recherche gallica###
        elif ('sru' in request or 'SRU' in request):
            request = '##GallicaSearchEngine'+request
            requests[i]['request_tag'] = 'GallicaSearchEngine'
        elif ('und' in request and 'search' in request):
            if (pos4 > pos3):
                request = '##GallicaSearchEngine'+request
                requests[i]['request_tag'] = 'GallicaSearchEngine'
            elif (pos3 > pos4):
                request = '##CollectionNavigation'+request
                requests[i]['request_tag'] = 'CollectionNavigation'
        elif ('Search' in request and 'lang' in request):
            request = '##GallicaSearchEngine'+request
            requests[i]['request_tag'] = 'GallicaSearchEngine'
        elif ('Refinement' in request):
            request = '##GallicaSearchEngine'+request
            requests[i]['request_tag'] = 'GallicaSearchEngine'
        elif ('Search' in request or 'search' in request):
            request = '##GallicaSearchEngine'+request
            requests[i]['request_tag'] = 'GallicaSearchEngine'
        ### accès au blog gallica###
        elif ('und' in request and 'blog' in request):
            if (pos4 > pos7):  # acceuil before und
                request = '##AccessGallicaBlog'+request
                requests[i]['request_tag'] = 'AccessGallicaBlog'
            elif (pos7 > pos4):
                request = '##CollectionNavigation'+request
                requests[i]['request_tag'] = 'CollectionNavigation'
        elif ('blog' in request):
            request = '##AccessGallicaBlog'+request
            requests[i]['request_tag'] = 'AccessGallicaBlog'
        ### navigation dans les collections gallica###
        elif ('und' in request or 'livres' in request or 'cartes' in request or 'enregistrements-sonores' in request or
              'essentiels' in request or 'presse-et-revues' in request or 'lang' in request):
            request = '##CollectionNavigation'+request
            requests[i]['request_tag'] = 'CollectionNavigation'

        else:
            request = '##Outliers'+request
            requests[i]['request_tag'] = 'Outliers'
    return requests 

def save_to_db(client_id, index, requests, collection_db):
    field = "sessions."+str(index)+".requests"
    response = collection_db.update_one({'client_id': client_id}, {
                                     '$set': {field: requests}})

def trace_handler(trace):
    req = ""
    requests = trace["sessions"]["requests"]
    req_len = len(requests)
    for i, request in enumerate(requests):
        req += request["request_tag"]
        if i < req_len-1:
            req += ","
    return f"{trace['client_id']};{req}"
