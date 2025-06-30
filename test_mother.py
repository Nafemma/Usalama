from modules.mother.mother_module import *

if __name__ == "__main__":
    info = calculate_pregnancy_info("2024-12-01")
    print(info)
    print(get_health_tip(info["week_number"]))
    print(log_mood("mother001", "Happy and glowing"))
    print(check_danger_signs("vomitting"))
    print(logout())
