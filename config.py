DEBUG = True
mobile = False

search_term = "Купить постельное бельё"

link_masks = [
    r".",
]

index = 3

if __name__ == "__main__":
    from main import main
    main()