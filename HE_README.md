//1. Создать массив с набором слов (10-20 слов, должны встречаться повторяющиеся).
// Найти и вывести список уникальных слов, из которых состоит массив (дубликаты не считаем).
// Посчитать сколько раз встречается каждое слово.

 String[] strarr= "bukafki".split(" ");
 ArrayList<String> string_list = new ArrayList<String>();
  for(int i=0; i < strarr; i++)
  {
    String word = strarr [i];
                                                                                                                            if( string_list.containts(word) == false ) \\проверка науникальность{ string_list.add(word)
 }
  }
     int unikum = string_list.size()



||
public static void main(String[] args) {

String[] words = {
"впавпвап","ппппп","выаываы","вввв","5435","Jdssfs","id","JavaScript","fddsf","id","dfdsfsdf","id","noze","uno","noze","hhhhh","bigL","noze"};
HashMap<String, Integer> mash = new HashMap<>();

for(String word: words) {
 Integer res = mash.get(word);
 mash.put(word, res == null ? 1 : res + 1);
 }
 System.out.println(mash);

//*Написать простой класс ТелефонныйСправочник, который хранит в себе список фамилий и телефонных номеров. В этот телефонный справочник с помощью метода add() можно добавлять записи. С помощью метода get() искать номер телефона по фамилии. Следует учесть, что под одной фамилией может быть несколько телефонов (в случае однофамильцев), тогда при запросе такой фамилии должны выводиться все телефоны *\

public static void main(String args[]) {
Phonebook phonebook = new Phonebook();

phonebook.add("Муаммад", 8-800-555-3535);
phonebook.add("Влад", 8-999-000-9955);
phonebook.add("Абдулла", 8-999-555-8855);
phonebook.add("Костик", 9-555-555-5555);
phonebook.add("Толиан", 8-555-555-5555);

phonebook.add("Лиана", 8-855-555-5555);
phonebook.add("Толкан", 8-544-355-2255);

phonebook.get("Муаммад ");
phonebook.get("Костик ");
phonebook.get("Влад");
phonebook.get("Толиан");
phonebook.get("Толкан");
}
}
