/*
 * Author: Group A
 * Course: CSE 4081, Section 01, Fall 2016
 * Project: project_arithmetic coding
 */

public class RandomStrings {
    private static String str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789~`!@#$%^&*()_-+=/{}[]|.,;:?'<>\\ \"";
	
    public static int getRandom (int count) {
        return (int) (Math.random() * (count));
    }
	
    public static String getRandomString (int length) {
        StringBuffer sb = new StringBuffer();
        for (int i = 0; i < length; i++) {
            int position = getRandom(str.length());
            sb.append(str.charAt(position));
        }
        return sb.toString();
    }

    public static void main (String[] args) {
        int n = Integer.parseInt(args[0]);
        System.out.println(getRandomString(n));
    }
}
