# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import lib.pymysql as db
import string
import random

def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        settings.mysql_host, 
        settings.mysql_user, 
        settings.mysql_passwd, 
        settings.mysql_schema)
    
    return con

def  findTrips(x,a,b):
    
    # Create a new connection
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()
    ret_val=[("Cost_per_person", "max_num_participants","Reservation_id","Empty_Seats","Guider_name","Guider_surname","Driver_name","Driver_surname")]
    try:
        for c in range(1,179):
            sql=""" SELECT  cost_per_person,max_num_participants,COUNT(DISTINCT Reservation_id),max_num_participants-COUNT(DISTINCT Reservation_id) AS Empty_Seats,a.surname,a.name,b.surname,b.name
                    FROM  travel_agency_branch,trip_package,offer,reservation,drivers,travel_guide,employees a , employees b
                    WHERE trip_package.trip_package_id = '%d'AND travel_agency_branch.travel_agency_branch_id='%d'
                    AND trip_start>'%s' AND trip_start <= '%s'
                    AND trip_package.trip_package_id=offer.trip_package_id 
                    AND offer.trip_package_id=reservation.offer_trip_package_id
                    AND reservation.travel_agency_branch_id=travel_agency_branch.travel_agency_branch_id
                    AND a.travel_agency_branch_travel_agency_branch_id=travel_agency_branch.travel_agency_branch_id
                    AND b.travel_agency_branch_travel_agency_branch_id=travel_agency_branch.travel_agency_branch_id
                    AND a.employees_AM=drivers.driver_employee_AM AND b.employees_AM=travel_guide.travel_guide_employee_AM
                    """ %  (int(c) , int(x) , a ,b)
            cur.execute(sql)
            results=cur.fetchone()
            if(results != (None,None,0,None,None,None,None,None)):
                ret_val.append(results)
    except:
        ret_val=("false")
    return ret_val


def findRevenue(x):
    
   # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()
    ret_val = [("INCOME", "Branch_id","reservations","Employees","Salaries")]
    try:
        if(x== "ASC"):
            sql=""" SELECT (COUNT(DISTINCT Reservation_id)*offer.cost) AS Income,travel_agency_branch.travel_agency_branch_id,COUNT(DISTINCT Reservation_id) AS Reservations,COUNT(DISTINCT employees_AM) AS Employees,SUM(DISTINCT salary) AS Salaries
                    FROM travel_agency_branch,reservation,trip_package,traveler,employees,offer
                    WHERE travel_agency_branch_travel_agency_branch_id=travel_agency_branch.travel_agency_branch_id
                    AND reservation.travel_agency_branch_id=travel_agency_branch.travel_agency_branch_id
                    AND traveler_id=Customer_id AND offer.trip_package_id=trip_package.trip_package_id
                    AND offer.trip_package_id=reservation.offer_trip_package_id
                    GROUP BY(travel_agency_branch.travel_agency_branch_id)
                    ORDER BY  Income  ;"""
        elif(x == "DESC"):
            sql=""" SELECT (COUNT(DISTINCT Reservation_id)*offer.cost) AS Income,travel_agency_branch.travel_agency_branch_id,COUNT(DISTINCT Reservation_id) AS Reservations,COUNT(DISTINCT employees_AM) AS Employees,SUM(DISTINCT salary) AS Salaries
                    FROM travel_agency_branch,reservation,trip_package,traveler,employees,offer
                    WHERE travel_agency_branch_travel_agency_branch_id=travel_agency_branch.travel_agency_branch_id
                    AND reservation.travel_agency_branch_id=travel_agency_branch.travel_agency_branch_id
                    AND traveler_id=Customer_id AND offer.trip_package_id=trip_package.trip_package_id
                    AND offer.trip_package_id=reservation.offer_trip_package_id
                    GROUP BY(travel_agency_branch.travel_agency_branch_id)
                    ORDER BY  Income  DESC ;"""
        cur.execute(sql)
        results=cur.fetchall()
        for row in results:
            ret_val.append(row)
    except:
        ret_val=("false",)

    return ret_val

def bestClient(x):

    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()
    ret_val=[("Cost","Name","Surname","numofcountries","numofcities","sights")]
    try:
        sql=""" SELECT SUM(offer.cost) AS Revenue,traveler.name,surname,COUNT(DISTINCT country),COUNT(DISTINCT destination.name)
                FROM traveler,reservation,offer,trip_package,tourist_attraction,destination,trip_package_has_destination
                WHERE Customer_id=traveler_id AND reservation.offer_trip_package_id=offer.trip_package_id AND offer.trip_package_id=trip_package.trip_package_id
                AND tourist_attraction.destination_destination_id=destination.destination_id 
                AND destination.destination_id=trip_package_has_destination.destination_destination_id
                AND trip_package_has_destination.trip_package_trip_package_id=trip_package.trip_package_id
                GROUP BY(traveler_id)
                ORDER BY Revenue DESC"""
        cur.execute(sql)
        results=cur.fetchone()
        ret_val.append(results)
        sql2="""SELECT DISTINCT tourist_attraction.name
                FROM traveler,reservation,offer,trip_package,tourist_attraction,destination,trip_package_has_destination
                WHERE Customer_id=traveler_id AND reservation.offer_trip_package_id=offer.trip_package_id AND offer.trip_package_id=trip_package.trip_package_id
                AND tourist_attraction.destination_destination_id=destination.destination_id 
                AND destination.destination_id=trip_package_has_destination.destination_destination_id
                AND trip_package_has_destination.trip_package_trip_package_id=trip_package.trip_package_id
                AND traveler.name="%s" AND traveler.surname="%s" """ % (results[1] , results[2] )
        cur.execute(sql2)
        results=cur.fetchall()
        for row in results:
            ret_val.append(("","","","","",row[0]))  
    
    except:
        ret_val=("false")
        
    return ret_val
    

def giveAway(N):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()
    try:
        sql=""" select traveler.traveler_id
                from traveler
                ORDER BY traveler_id ASC"""
        cur.execute(sql)
        id_pool=cur.fetchall()
        id_pool=list(id_pool)
        ret_val=[("message",)]
        for i in range(int(N)):
            traveler_id=random.randint(0, len(id_pool))
            id_pool.pop(traveler_id)
            sql="""SELECT DISTINCT trip_package.trip_package_id
                    FROM trip_package,traveler,reservation,offer
                    WHERE reservation.Customer_id=traveler.traveler_id AND traveler_id='%d' 
                    AND reservation.offer_trip_package_id=offer.trip_package_id
                    AND offer.trip_package_id=trip_package.trip_package_id"""% (int(traveler_id))
            cur.execute(sql)
            Used_Package_ids=cur.fetchall()
            while True :
                Id_of_Package = random.randint(1,179)
                if Id_of_Package not in Used_Package_ids:
                    break
            ####
            ####Finding offer
            if len(Used_Package_ids) > 1 : 
                offer=0.75
                Cat_offer="group-discount" 
            else: 
                offer=1
                Cat_offer="full-price"
            
            sql2="""select cost_per_person
                    from trip_package
                    where trip_package_id='%d'"""%(int(Id_of_Package))
            cur.execute(sql2)
            cost_per_person=cur.fetchall()
            sql= """select offer.offer_id
                    from offer
                    ORDER BY offer_id DESC"""
            cur.execute(sql)
            first=cur.fetchone()
            offer_id=first[0]+1
            ###Inserting offer
            ###
            sql3="""
                    INSERT INTO offer(offer_id,offer_start,offer_end,cost,description,trip_package_id,offer_info_category)
                    VALUES('%d', '%s', '%s', '%d','%s','%d','%s')
                    """ %(int(offer_id),"2022-09-13","2022-09-17",int(cost_per_person[0][0]*offer),"Happy traveler tour",int(Id_of_Package),Cat_offer)
            cur.execute(sql3)
            con.commit()      
            ####
            ####finding destination
            sql4="""SELECT DISTINCT destination.name
                    FROM trip_package,trip_package_has_destination,destination
                    WHERE trip_package_id='%d' AND trip_package.trip_package_id=trip_package_has_destination.trip_package_trip_package_id
                    AND destination_id= trip_package_has_destination.destination_destination_id"""%(int(Id_of_Package))
            cur.execute(sql4)
            dest=cur.fetchall()
            ###
            ###finding name
            sql5=""" select traveler.name ,traveler.surname
                    from traveler
                    where traveler.traveler_id='%d'
                    """ %(int(traveler_id))
            cur.execute(sql5)
            name=cur.fetchall()
            sql="""select offer_id,offer_start,offer_end,cost,description,trip_package_id,offer_info_category
                from offer
                where offer_id='%d' """ % (int(offer_id))
            cur.execute(sql)
            new_offer=cur.fetchone()
            message="""Congratulations '%s'
            Pack your bags and get ready to enjoy the '%s"! At ART TOUR travel we acknowledge you as a valued customer and we’ve selected the most incredible
            tailor-made travel package for you. We offer you the chance to travel to '%s' at the incredible price of '%d'. Our offer ends on '%s'. Use code
            '%d' to book your trip. Enjoy these holidays that you deserve so much!
            """%(name[0][0],new_offer[4],dest,int(new_offer[3]),new_offer[2],int(new_offer[0]))
            ret_val.append((message,))
                
    except:
        ret_val=("false")
        
    return ret_val


