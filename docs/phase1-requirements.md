<h3 align="center"> Project Phase 1</h3>

<h1 align="center"> Physical Education Centre (PEC)</h1>
<h2 align="center"> Team: Samachara_Kendhram</h1>

**Team Members:**
- [Dileepkumar Adari] (2022101007)
- [Revanth Reddy] (2022101049)
- [Keshav] (2022101123)
- [Ritvik] (2022111034)


## INTRODUCTION TO MINI-WORLD
<p align="justify">
Our Mini-world is focused on enhancing the experience of the Physical Education Center (PEC), a vital part of the university. It provides imformation for students and faculty, transforming the way they engage with fitness activities, sports, equipment, and events at the PEC. The database facilitates efficient management of fitness challenges, sports activities, equipments, events, attendance and more. It serves as a platform for the users to maintain the resources easy enhancing fitness, organizing events, and and active participation of students in sports of the PEC.</p>

## PURPOSE OF THE DATABASE

The PEC database serves as a centralized platform with the following objectives:

- **Efficient Credit Tracking:** It enables students to conveniently check their event participation and attendance, which is crucial for earning academic credits.

- **Challenge Winner Records:** The database records and highlights the winners of various fitness challenges, fostering a competitive and motivating environment within the university.

- **Equipment Availability:** It provides real-time information on the availability of sports and fitness equipment, ensuring that students and faculty members can make informed decisions when planning their activities.

- **Event Management:** Faculty members can utilize the database to organize and manage sports events efficiently.

- **Financial Analysis and Fund Maintenance:** For the administration, the database offers tools for financial analysis, helping in the allocation and maintenance of funds for PEC operations.

- **PEC Center Oversight:** The PEC Head can maintain and supervise the entire PEC's operation, ensuring that it operates smoothly and efficiently.

- **Customized User Access:** Other users, such as trainers, coaches, and maintenance staff, can have access tailored to their specific roles and requirements.


## USERS OF THE DATABASE

The PEC database can be used by these potential Users:

- **Students:** Students use the database to track their event participation, attendance, and challenge results, which influence their academic credits.

- **Faculty Members:** Faculty members primarily rely on the database to participate and spectate sports events and enjoy the sports and also uses for the availability of GYM or fitness equipment.

- **Administration:** Administrative staff uses the database for financial analysis, budget allocation, and the overall maintenance of PEC operations.

- **PEC Head:** The PEC Head maintains and oversees the entire PEC operation, ensuring it functions efficiently like salaries, student attendance, fund allocation etc.

- **Trainers and Coaches:** Trainers and coaches use the database to monitor students progress (attendance), plan training sessions, and assign fitness challenges.

- **Maintenance Staff:** Maintenance staff can access the database to manage equipment maintenance, event schedules and repairs.

- **Other Users:** Users with specific roles (like sports secretary) and access needs can use the database according to their requirements.

## APPLICATIONS OF DATABASE

The PEC database serves various applications:

- **Credit Tracking:** Students can review their event participation , events schedule, availability of equipment and attendance to earn academic credits.

- **Challenges Winners:** Recording and highlighting winners of fitness challenges to encourage participation.

- **Equipment Management:** Real-time tracking of sports and fitness equipment availability.

- **Event Organization:** PEC can efficiently manage and organize sports events within the university and can ensure they are intact and flexible with academics.

- **Financial Analysis:** The administration utilizes the database for financial analysis and fund allocation.

- **Operations Oversight:** The PEC Head uses the database to ensure the smooth operation of the PEC and timely work of the staff.

- **Training and Coaching:** Trainers and coaches monitor students fitness and plan training sessions and events.

- **Maintenance and Repairs:** Maintenance staff can keep equipment in working order, ensuring safety and functionality.

- **Customized Access:** Users with specific roles can access the database as needed, based on their responsibilities like monitoring events.

These applications and functionalities collectively contribute to the enhancement and effective management of the Physical Education Center within the university.


## Database Requirements

**Strong Entity Types:**
1. **Students:**
   - Student ID (Primary Key, Integer, Not Null)
   - Name (Composite Attribute)
     - First Name (Simple Attribute, String, Not Null, 50 characters)
     - Last Name (Simple Attribute, String, Not Null, 50 characters)
   - Date of Birth (Simple Attribute, Date, Not Null)
   - Contact Information (Simple Attribute, String, Not Null, 100 characters)
   - Course-Year (Simple Attribute, String, Not Null, 20)
   - Department (Simple Attribute, String, Not Null, 20)
   - Selected Sport (Simple Attribute, String, Not Null, 50 characters)
   - Age (Derived Attribute, Integer, Not Null)
   - Attendance (Simple Attribute, Integer, Not Null)
   - Completed Credits (Simple Attribute, Integer, Not Null)
   - Medical History (Complex Attribute)

2. **Staff:**
   - Staff ID (Primary Key, Integer, Not Null)
   - Name (Composite Attribute)
     - First Name (Simple Attribute, String, Not Null, 50 characters)
     - Last Name (Simple Attribute, String, Not Null, 50 characters)
   - Type (Simple Attribute, String, Not Null, 50 characters)
   - Position (Multi valued Attribute, strings, Not Null, 100 characters)
   - Contact Information (Simple Attribute, String, Not Null, 100 characters)
   - Employment Start Date (Simple Attribute, Date, Not Null)
   - Experience (Derived Attribute, Integer, Not Null)
   - Salary (Simple Attribute, Float, Not Null)
   - Pay Status (Simple Attribute, String, Not Null, 20 characters)
   - Responsibilities (Complex Attribute - composite and multi valued)

3. **Fitness Challenges:**
   - Challenge ID (Primary Key, Integer, Not Null)
   - Challenge Name (Simple Attribute, String, Not Null, 100 characters)
   - Description (Simple Attribute, String, Not Null, 500 characters)
   - Schedule (Simple Attribute, Date, Not Null)
   - Location (Simple Attribute, String, Not Null, 100 characters)
   - Maximum Participants (Simple Attribute, Integer, Not Null)
   - Winner (Simple Attribute, String, 100 characters)
   - Prize (cost) (Simple Attribute, Float, Not Null)
   - Registration Deadline (Simple Attribute, Date, Not Null)

4. **Equipment:**
   - Equipment ID (Primary Key, Integer, Not Null)
   - Equipment Type (Simple Attribute, String, Not Null, 100 characters)
   - Quantity (Simple Attribute, Integer, Not Null)
   - Condition (Simple Attribute, String, Not Null, 100 characters)
   - Last Upgrade (Simple Attribute, Date, Not Null)
   - Maintenance Logs (Multi-Valued Attribute, String)

5. **Sports:**
   - Sport ID (Primary Key, Integer, Not Null)
   - Sport Name (Simple Attribute, String, Not Null, 100 characters)
   - Location (Simple Attribute, String, Not Null, 100 characters)
   - Rules and Regulations (Multi-Valued Attribute, String)
   - Capacity (Simple Attribute, Integer, Not Null)
   - Manager (Simple Attribute, String, 100 characters)
   - Required Equipment (Complex Attribute)
   - Current Participants (Simple Attribute, Integer, Not Null)
   - Available Time Slots (Simple Attribute, String, 100 characters)

6. **Funds:**
   - Fund ID (Primary Key, Integer, Not Null)
   - Amount (Simple Attribute, Float, Not Null)
   - Date (Simple Attribute, Date, Not Null)
   - Reason (Simple Attribute, String, Not Null, 200 characters)
   - Status (Simple Attribute, String, Not Null, 50 characters)

**Weak Entity Types:**
1. **Injuries/Health Records:**
   - Student ID (Key Attribute, Integer, Not Null)
   - Date and Time (Key Attribute, Date, Not Null)
   - Type (Simple Attribute, String, Not Null, 100 characters)
   - Severity (Simple Attribute, String, Not Null, 100 characters)
   - Treatment (Simple Attribute, String, Not Null, 500 characters)
   - Recovery Time (Simple Attribute, String, Not Null, 100 characters)

2. **Equipment Reservations:**
   - Reservation ID (Key Attribute, Integer, Not Null)
   - Equipment ID (Key Attribute, Integer, Not Null)
   - Date and Time (Simple Attribute, Date, Not Null)
   - Price (Simple Attribute, Float, Not Null)
   - Quantity (Simple Attribute, Integer, Not Null)
   - Expected Arrival (Simple Attribute, Date, Not Null)
   - Reservation Status (Simple Attribute, String, Not Null, 50 characters)


**Relationship Types:**
**Participating Constraints and Degrees of Relationships:**

1. **Enroll:**
    - Students (0, N) enroll in (1, N) Fitness Challenges
        Constraints: A student can enroll in one or more fitness challenges. Each fitness challenge can have one or more enrolled students. 
        Degree of Relationship: 2

2. **Manage:**
    - Staff members (0, N) manage (1, N) Fitness Challenges
        Constraints: A staff member can manage one or more fitness challenges. Each fitness challenge is managed by one or more staff members. 
        Degree of Relationship: 2

3. **Utilize:**
    - Students and staff (0, N) utilize (0, N) Equipment
        Constraints: Both students and staff can utilize zero or more equipment items, and each equipment item can be utilized by zero or more students and staff. 
        Degree of Relationship: 2

4. **Participate:**
    - Students (0, N) participate in (1, N) Events
        Constraints: A student can participate in one or more events. Each event can have one or more participating students. 
        Degree of Relationship: 2

5. **Organize:**
    - Staff members (0, N) organize (1, N) Events
        Constraints: A staff member can organize one or more events. Each event is organized by one or more staff members. 
        Degree of Relationship: 2

6. **Reserve:**
    - Students and staff (0, N) make reservations (0, N) for Equipment
        Constraints: Both students and staff can make reservations for zero or more equipment items, and each equipment item can be reserved by zero or more students and staff. 
        Degree of Relationship: 2

7. **Have:**
    - Students (1, N) have (0, N) injury records
        Constraints: Each student can have zero or more injury records. 
        Degree of Relationship: 2

8. **Supervision:**
    - Staff (in the role of supervisor) supervise (1, N) other staff (in the role of workers)
        Constraints: A staff member in the role of supervisor can supervise one or more staff members in the role of workers. 
        Degree of Relationship: 1

9. **Trains:**
    - Staff (Trainer) (1, N) trains (1, N) in Sports (1, 1) taken by Students
        Constraints: Each faculty member teaches one or more courses to one or more students. Each course is taught by one faculty member to one or more students. 
        Degree of Relationship: 3



# Functional Requirements

## Modification

### Insert

- **Add new student records to the collection:** This includes personal details related to "Students" entity.
- **Add new staff members to the collection:** This involves staff roles, contact information, and employment details related to the "Staff" entity.
- **Record new fitness challenges and programs in the collection:** Related to "Fitness Challenges" entity.
- **Include information about the available equipment in the collection:** This specifies type, quantity, and availability related to the "Equipment" entity.
- **Add new events to the collection:** This provides names, dates, and descriptions related to the "Events" entity.
- **Include sports activities in the collection:** This details their schedules related to the "Sports" entity.
- **Record information about the physical facilities and spaces within the PEC in the collection:** Related to "Facilities and Spaces" entity.
- **Allow reservations for equipment, facilities, and event participation to be added to the collection:** Related to "Equipment Reservations" entity.

### Delete

- **Remove student records from the collection when they are no longer associated with the PEC:** Related to "Students" entity.
- **Delete staff members' information from the collection if they leave their positions:** Related to "Staff" entity.
- **Remove fitness challenges or programs from the collection that are no longer offered:** Related to "Fitness Challenges" entity.
- **Manage the availability of equipment in the collection:** This involves deleting some items which are    unavailable or out of service related to the "Equipment" entity.
- **Delete event details from the collection when events are canceled or completed:** Related to "Events" entity.
- **Remove sports activities from the collection that are no longer available:** Related to "Sports" entity.
- **Delete records of facilities and spaces within the PEC from the collection:** Related to "Facilities and Spaces" entity.
- **Cancel reservations for equipment, facilities, and event participation in the collection:** Related to "Equipment Reservations" entity.

### Update

- **Modify student information in the collection, including contact details or fitness challenge enrollment:** Related to "Students" entity.
- **Update staff records in the collection to reflect changes in roles or contact information:** Related to "Staff" entity.
- **Adjust the details of fitness challenges and programs in the collection, including schedules and locations:** Related to "Fitness Challenges" entity.
- **Update equipment information in the collection, such as maintenance status and availability:** Related to "Equipment" entity.
- **Modify event details in the collection, including dates, locations, and descriptions:** Related to "Events" entity.
- **Update information about sports activities in the collection, including schedules and rules:** Related to "Sports" entity.
- **Modify records of facilities and spaces within the PEC in the collection:** Related to "Facilities and Spaces" entity.
- **Change or update existing reservations for equipment, facilities, and event participation in the collection:** Related to "Equipment Reservations" entity.

## Retrieval

### Selection

- **Retrieve a list of students enrolled in a specific fitness challenge from the collection:** Related to "Fitness Challenges" entities.
- **Retrieve a list of students enrolled in a Sport from the collection:** Related to "Sports" entities.
- **Query the collection to find staff members responsible for managing particular fitness challenges:** Related to "Staff" and "Fitness Challenges" entities.
- **Find available equipment of a specific type in the collection:** Related to "Equipment" entity.
- **Retrieve the list of events happening on a particular date from the collection:** Related to "Events" entity.
- **Get a list of fitness challenges scheduled for a specific period from the collection:** Related to "Fitness Challenges" entity.
- **Retrieve the list of sports activities offered on a given day from the collection:** Related to "Sports" entity.
- **Retrieve reservations made on a data from the collection:** Related to "Equipment Reservations" entity.

### Projection

- **Query the collection to enable users to search by a particular attribute(column):** For example, "IDs and Names of all students participating in a particular sport" related to "Students" entities.

### Aggregate

- **Perform an aggregation operation on the collection to calculate the sum of all funds released in a month:** Related to the "Funds" entity.

### Search

- **Search for entries in the collection (partial text match), matching subparts of the entries:** For example, searching for "Manager" to find employees with "Manager" in their job title, related to "Staff" entity.


## Analysis

- **Calculate the average number of students enrolled in fitness challenges from the collection:** "Fitness Challenges" entities.
- **Analyze the staff workload by determining their involvement in fitness challenges using the collection:** Related to "Staff" and "Fitness Challenges" entities.
- **Determine the most popular types of equipment among students and staff by analyzing the collection:** Related to "Equipment" entity.
- **Evaluate the success of events based on participation and feedback from the collection:** Related to "Events" entity.
- **Analyze participation trends in sports activities using the collection:** Related to "Sports" entity.
- **Monitor facility usage and identify peak hours by analyzing the collection:** Related to "Facilities and Spaces" entity.
- **Analyze reservation patterns and demand for facilities and equipment from the collection:** Related to "Equipment Reservations" entity.

## Summary

This system seeks to transform the way students and faculty engage with the PEC, offering efficient management tools for various aspects such as fitness challenges, sports activities, equipment, attendance and events. By providing a centralized platform, it caters to a diverse user base, including students, faculty, and administrative staff, each with tailored access. The database requirements contained entity types and relationships, supporting data organization and retrieval. Functional requirements define key operations related to data modification, retrieval, and analysis. This project's aim is to enhance the PEC's capabilities and user experience, with further enhancements planned for the future.


## Enhancements of Existing Database

The database that the PEC now have only the attendance and the equipment, the database we are developing is the upgrade for the PEC which makes much improvement and ease of maintenance and access for all the required users and the enhancement of the Physical Education.