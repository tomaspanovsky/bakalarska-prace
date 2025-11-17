def create_tent_area(num_visitors):

    capacity = num_visitors // 3
    
    if capacity < 1:
        area = [[]]
    else:
        area = []

    for i in range(capacity):
        area.append([])

    return area

def print_stany(area):
    print(area)

