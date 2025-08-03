import csv
import xlsxwriter
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='app.log'  
)

logger = logging.getLogger(__name__)

class xlsx_csv():
    def __init__(self,username,spisok):
        self.spisok = spisok
        self.username = username 

    def add_to_csv(self):
        with open( 'newfile.csv','a',encoding = 'utf-8',newline='')as file:
            writer = csv.writer(file)
            writer.writerow([self.username])
            for row in self.spisok:
                if not row: continue
                writer.writerow([row])
        logger.info('CSV файл успешно создан')
        
    def add_to_xlsx(self):
        workbook = xlsxwriter.Workbook('im_file.xlsx')
        worksheet= workbook.add_worksheet('Я лист')
        row = 1
        worksheet.write(0,0,self.username)
        for item in (self.spisok):
            if not item: continue
            item = str(item)
            worksheet.write(row,0,item)
            row+=1
        workbook.close()
        logger.info('XLSX файл успешно создан')


