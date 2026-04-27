# SpotlightAI
**1. Introduction**
Spotlight AI is an intelligent Assessment for Learning (AFL) classroom tool that uses rule-based Q-learning. to adaptively select students and present questions generated using AI models from the materials uploaded by the teachers of varying difficulty based on their learning history. The system aims to personalize assessment while ensuring fair participation, attention, and equal learning opportunities for all students.
In addition, Spotlight AI supports teachers by providing data-driven analysis of student performance and engagement. This analysis helps teachers identify students who require additional support and make informed instructional decisions to enhance the overall learning experience.
<img width="983" height="425" alt="image" src="https://github.com/user-attachments/assets/b0b2d2bc-4d08-4249-9ead-7c83187071da" />
**2. Dataset and Pre-processing**
Student and Classroom Data:
●	Dataset Type: Images of students’ faces for recognition, along with quiz performance records stored in Firebase.
●	Input:
○	Student face images (jpg, png)
○	Uploaded quiz materials (PDF, DOCX, PPTX)
○	Student responses to AI-generated questions
●	Output:
○	Face embeddings for recognition
○	Quiz scores, turns, difficulty history
○	Emotion detection labels (e.g., happy, sad, neutral)
●	Data Volume:
○	30–50 students per classroom
○	Quiz sessions generate dynamic datasets for reinforcement learning
Pre-processing Steps:
●	Images resized and converted to arrays via OpenCV
●	Embeddings extracted and stored in .npy files
 <img width="981" height="419" alt="image" src="https://github.com/user-attachments/assets/58fdd7e6-7a6c-4412-b8d6-f4a859a5b770" />
●	Text from uploaded materials extracted using docx2txt, PyPDF2, and python-pptx
●	Student scores normalized and stored for reinforcement learning.
 <img width="981" height="577" alt="image" src="https://github.com/user-attachments/assets/47dbdb10-7401-4e8a-b393-93e10ef93851" />
**3. Approach**

System Modeling:
1.	Priority Based on Minimum Turns: For each quiz session, the system selects students who have had the fewest turns (least number of questions answered) to participate first.
●	This ensures fair distribution of questions among all students and prevents some students from being skipped or overrepresented.
●	It also allows the Q-learning algorithm to update states and Q-values evenly across the class, improving the accuracy of adaptive difficulty for all students.
 <img width="975" height="381" alt="image" src="https://github.com/user-attachments/assets/2bf9f9fe-5b44-4a15-b2a4-3298a51fc3d0" />
2.	Adaptive Quiz Generation: Reinforcement Learning (Q-learning) selects questions based on:
○	Student’s current score (state: LOW, MEDIUM, HIGH)
○	Past performance
○	ε-greedy policy balances exploration vs exploitation
●	Algorithms:
○	Q-Learning: Adaptive question selection and student selection
○	Firebase Firestore: Real-time storage and retrieval of student progress
Q-Table Structure:

 	{
    	"LOW":    {"Easy": 0.0, "Medium": 0.0, "Hard": 0.0},
    	"MEDIUM": {"Easy": 0.0, "Medium": 0.0, "Hard": 0.0},
    	"HIGH":   {"Easy": 0.0, "Medium": 0.0, "Hard": 0.0}
}
●	States: Represent the student’s current skill level (LOW, MEDIUM, HIGH).
●	Actions: Represent the difficulty of the next question (Easy, Medium, Hard).
●	Q-values: Represent the expected reward for presenting a particular difficulty to a student in a given state.
Reward Rules:
●	The system implements rule-based rewards to guide learning:
○	LOW state: Correct Easy → high reward; Hard → negative reward (to avoid frustration)
○	MEDIUM state: Correct Medium → high reward; Hard → moderate reward
○	HIGH state: Correct Hard → high reward; Easy → low reward (discourages under-challenging)
●	This ensures students are challenged appropriately without being overwhelmed.
<img width="981" height="512" alt="image" src="https://github.com/user-attachments/assets/cc9272ee-71c4-4785-b871-6a699f332864" />
Q-Value Update (Reinforcement Learning):
●	After each question, the Q-value is updated using:
Q(s,a)←Q(s,a)+α⋅(R−Q(s,a))
○	s: Current student state (LOW, MEDIUM, HIGH)
○	a: Selected action (question difficulty)
○	R: Reward (+10 for correct, -5 for incorrect, modified by rules)
○	α (alpha): Learning rate (controls how fast the system adapts)
●	This approach balances exploration vs exploitation using an ε-greedy policy:
○	With probability ε, a random difficulty is chosen (exploration)
○	Otherwise, the difficulty with the highest Q-value is selected (exploitation)
Rule Constraints:
●	Certain rules are enforced to prevent unrealistic jumps:
○	LOW state cannot be assigned a Hard question directly
○	High-performing students are occasionally presented easier questions to reinforce knowledge.
 <img width="1040" height="429" alt="image" src="https://github.com/user-attachments/assets/232e8a9f-d9c0-4f88-ad8b-2fb08fe744dd" />
**4. Evaluation and Analysis**
Evaluation Metrics:
●	Quiz Accuracy: Number of correctly answered questions per student
●	Adaptive Difficulty: Correct selection of question difficulty based on performance
●	Completion Rate: Percentage of students completing quizzes
●	RL Performance: Q-table updates reflecting learning and adaptation
 
 <img width="1030" height="403" alt="image" src="https://github.com/user-attachments/assets/50664716-63db-45fa-8b7a-4c062fe9ff83" />
 <img width="1055" height="442" alt="image" src="https://github.com/user-attachments/assets/30ca5a77-d812-443c-b9e0-214272605b3e" />
 <img width="1055" height="314" alt="image" src="https://github.com/user-attachments/assets/de3cd058-6725-4cd7-9c49-69c1dc19b8ea" />
**5. Conclusion**

The Spotlight AI system demonstrates an effective approach to personalized learning by dynamically adapting question difficulty for each student. Leveraging Q-learning with rule-based rewards, the system selects students with the minimum participation first, ensuring fairness and engagement. Real-time performance tracking, score progression, and difficulty adjustments allow teachers to monitor and support students effectively. Integration with Firebase for data storage and face recognition for student identification makes the system scalable and automated. Overall, Spotlight AI proves the potential of AI-driven adaptive learning, with future enhancements possible through advanced reinforcement learning strategies and richer analytics for improved educational outcomes.

