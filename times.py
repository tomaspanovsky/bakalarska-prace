def format_time_minutes_to_hours(minutes):
    minutes = int(minutes)
    minutes = minutes % 1440
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def format_time_string_to_mins(string):
    hours, minutes = map(int, string.split(":"))
    total_minutes = hours * 60 + minutes
    return total_minutes

def get_real_time(env, start_time, future = None):

    if future:
        total_minutes = future + start_time
    else:
        total_minutes = int(env.now) + start_time
        
    return format_time_minutes_to_hours(total_minutes)
