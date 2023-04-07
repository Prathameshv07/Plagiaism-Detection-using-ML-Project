# Sem---VI-Project
**Project done in Sem - VI (TCSC)**

This project basically gets the text from web page text-box which is then formated where blank space is replaced by dot and then it is futher sent to query with the help of googlesearch package to check whether we found similarity between our text and the internet. If we found similarity the similar word are shown in another text box and it also does calculate the percentage of the similar word which are shown in another text box and we can also generate report on similar word found on the internet with specificing how many words are copied from which website with there percentage. 

And there is another part where you can check plagiarism between two files and get there similarity percentage with the help of kmp  (Knuth-Morris-Pratt) algorithm then it calculate the percentage of the similar word between two files which are then shown in another text box.

**Virtual Environment GUIDE**

Download virtual environment
```cmd
pip install virtualenv
```

To transfer all packages from the system to virtual environment
```cmd
virtualenv --system-site-packages C:\Users\PRATHAMESH\Downloads\Plagiarism-Detection\Final_Ver venv
```

Activate the environment by following command
```cmd
.\venv\Scripts\activate or activate.bat
```

Get all the packages inside req.txt
```cmd
python -m pip -r freeze > req.txt
```

List all the packages used in the current project
```cmd
pipreqs C:\Users\PRATHAMESH\Downloads\Plagiarism-Detection\Final_Ver
```

Install all the python packages
```cmd
python -m pip -r requirements.txt
```
