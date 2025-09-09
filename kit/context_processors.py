def kit_context(request):
    kit_item_count = 0
    if 'kit' in request.session:
        kit_item_count = len(request.session['kit'])
    return {'kit_context': {'kit_item_count': kit_item_count}}
