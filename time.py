def format_time_minutes_to_hours(minutes):
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"

def format_time_string_to_mins(string, day_start):
    hours, minutes = map(int, string.split(":"))
    total_minutes = hours * 60 + minutes
    return total_minutes - day_start

print(format_time_string_to_mins("15:00"))