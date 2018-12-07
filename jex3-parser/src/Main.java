import java.io.File;
import java.io.FileNotFoundException;
import java.io.PrintWriter;
import java.io.UnsupportedEncodingException;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.*;


public class Main {

    static HashMap<String, HashMap<String, Integer>> word_counts = new HashMap<String, HashMap<String, Integer>>();
    static HashSet<String> CONTEXT_TEGSET = new HashSet<>(Arrays.asList("VB", "VBD", "VBG", "VBN", "VBP", "VBZ",
        "NN", "NNP", "NNPS", "NNS",
        "JJ", "JJR", "JJS",
        "RB", "RBR", "RBS"));

    public static void main(String[] args) {
	// write your code here
        String parse_type = args[0];
        System.out.println(parse_type);
        String input_data =  System.getProperty("user.dir")+"/"+ args[1];
        String output_file = System.getProperty("user.dir")+"/" + args[2];
        String word_output = System.getProperty("user.dir")+"/" + args[3];
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        LocalDateTime now = LocalDateTime.now();
        System.out.println("started: " + now.format(formatter));
        int word_min_num = Integer.valueOf(args[4]);

        if (parse_type.equals("all")) {
            try {
                all_sentence_parse(input_data, output_file);
            } catch (Exception e)
            {
                System.out.print(e);
            }
        }
        else if (parse_type.equals("window")) {
            window_parse(input_data, output_file);
        }

        print_words(word_output, word_counts, word_min_num);
        now = LocalDateTime.now();
        System.out.println("finished: " + now.format(formatter));
    }

    private static void print_words(String output_file, HashMap<String, HashMap<String, Integer>> word_counts, int word_min_num) {
        try {
            File out = new File(output_file);
            PrintWriter writer = new PrintWriter(out, "UTF-8");
            for (Map.Entry<String, HashMap<String, Integer>> map : word_counts.entrySet())
            {
                int sum =0;
                for (Map.Entry<String, Integer> entry : word_counts.get(map.getKey()).entrySet()){
                    sum +=entry.getValue();
                }
                if(sum> word_min_num) {
                    for (Map.Entry<String, Integer> entry : word_counts.get(map.getKey()).entrySet()) {
                        if (entry.getValue() > 0)
                            writer.write(String.format("%s %d\n", entry.getKey(), entry.getValue()));
                    }
                }
            }
            writer.close();
        } catch (Exception e) {
            System.out.print(e);
        }
    }

    private static void window_parse(String input_data, String output_file) {

    }

    private static void all_sentence_parse(String input_path, String output_path) throws FileNotFoundException, UnsupportedEncodingException {
        File input_file = new File(input_path);
        final Scanner s = new Scanner(input_file);
        File output_file = new File(output_path);
        PrintWriter writer = new PrintWriter(output_file, "UTF-8");
        ArrayList<String> line_words = new ArrayList<>();
        while (s.hasNextLine()) {
            String file_line = s.nextLine();
            String[] line = file_line.split("\\s+");
            if (line.length > 1) {
                String word = line[1];
                String lamma = line[2];
                String word_tag = line[4]; //lemma's tag
                if (CONTEXT_TEGSET.contains(word_tag)) {
                    addToWordCounts(word, lamma);
                    line_words.add(word);
                }
            } else {
                for (int i =0; i<line_words.size(); i++) {
                    for (int j =0; j<line_words.size(); j++) {
                        if (i!=j) {
                            String line_word = line_words.get(i);
                            String context_word = line_words.get(j);
                            String string2file = line_word + ' ' + context_word + '\n';
                            writer.write(string2file);
                        }
                    }
                }
                line_words = new ArrayList<>();
            }
        }
        writer.close();
    }

    private static void addToWordCounts(String word, String lamma) {
        HashMap<String, Integer> map = word_counts.getOrDefault(lamma, new HashMap<String, Integer>());
        map.put(word, map.getOrDefault(word, 0 ) + 1);
        word_counts.put(lamma, map);
    }
}
