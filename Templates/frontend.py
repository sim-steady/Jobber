print("\n")
print("Welcome to the data janitors risk performance prediction services")
print("\n")
print("Would you like to enter the details manually or use a csv file?")
way=input("Please enter manual/csv: ")

#csv file reading
if way=="csv":
    user_data={}

    print("\n")
    fname=input("Please enter the name of the data file that you want to read the data from: ")
    with open(fname) as fhand:
        for line in fhand:
            lst=line.split()
            user_data[lst[0]]=lst[1:]

    print("Thank you, the file is now read.")
    username=input("Please enter the name of the user you want the prediction for: ")

    features=user_data[username]
print(25)
sskanasbdajksdkasbdkjasbdkjasbdkjasbdjasbdjkasdd
