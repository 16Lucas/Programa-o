import java.util.Scanner;

public class Exercicios {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        // 1. Escreva um programa que crie um vetor de números inteiros, receba 10 valores informados pelo usuário, imprima todos os valores pares e depois todos os valores ímpares.

        int[] numeros = new int[10];
        System.out.println("Digite 10 números inteiros:");
        for (int i = 0; i < 10; i++) {
            numeros[i] = sc.nextInt();
        }
        System.out.println("Números pares:");
        for (int num : numeros) {
            if (num % 2 == 0) {
                System.out.print(num + " ");
            }
        }
        System.out.println("\nNúmeros ímpares:");
        for (int num : numeros) {
            if (num % 2 != 0) {
                System.out.print(num + " ");
            }
        }
        
        // 2. Escreva um programa que leia 10 valores inteiros, informados pelo usuário e armazene-os em um vetor. Após isso, lendo o vetor uma única vez e sem criar outros vetores, mostre na tela a média dos valores armazenados no vetor ponderados pelos índices nos quais estão armazenados.
		
        int soma = 0, somaPesos = 0;
        for (int i = 0; i < 10; i++) {
            soma += numeros[i] * i;
            somaPesos += i;
        }
        System.out.println("\nMédia ponderada: " + (double) soma / somaPesos);
        
        // 3. Leia um valor e faça um programa que coloque o valor lido na primeira posição de um vetor de 10 posições. Em cada posição subsequente, coloque o dobro do valor da posição anterior. Por exemplo, se o valor lido for 1, os valores do vetor devem ser 1, 2, 4, 8 e assim sucessivamente. Mostre o vetor em seguida.
		
        System.out.print("\nDigite um valor para iniciar o vetor: ");
        int valor = sc.nextInt();
        int[] vetor = new int[10];
        vetor[0] = valor;
        for (int i = 1; i < 10; i++) {
            vetor[i] = vetor[i - 1] * 2;
        }
        System.out.println("Vetor gerado: ");
        for (int num : vetor) {
            System.out.print(num + " ");
        }
        
        // 4. Leia um valor X. Coloque este valor na primeira posição de um vetor N de 100 posições. Em cada posição subsequente de N (1 até 99), coloque a metade do valor armazenado na posição anterior, conforme o exemplo abaixo. Imprima o vetor N.
		
        System.out.print("\nDigite um valor X: ");
        double[] N = new double[100];
        N[0] = sc.nextDouble();
        for (int i = 1; i < 100; i++) {
            N[i] = N[i - 1] / 2;
        }
        System.out.println("Vetor N:");
        for (double num : N) {
            System.out.printf("%.4f ", num);
        }
        
        // 5. Faça um programa que leia um valor e apresente o número de Fibonacci correspondente a este valor lido. Lembre-se que os 2 primeiros elementos da série de Fibonacci são 0 e 1 e cada próximo termo é a soma dos 2 anteriores a ele. Todos os valores de Fibonacci calculados neste problema devem caber em um inteiro de 64 bits sem sinal.

        System.out.print("\nDigite um índice de Fibonacci: ");
        int fibIndex = sc.nextInt();
        long a = 0, b = 1, c = 0;
        if (fibIndex == 0) c = 0;
        else if (fibIndex == 1) c = 1;
        else {
            for (int i = 2; i <= fibIndex; i++) {
                c = a + b;
                a = b;
                b = c;
            }
        }
        System.out.println("Número de Fibonacci: " + c);
        
        // 6. Crie uma matriz bidimensional quadrada para armazenar 9 valores inteiros informados pelo usuário. Depois, calcule e mostre na tela o determinante da matriz.

        int[][] matriz = new int[3][3];
        System.out.println("\nDigite 9 valores para a matriz 3x3:");
        for (int i = 0; i < 3; i++) {
            for (int j = 0; j < 3; j++) {
                matriz[i][j] = sc.nextInt();
            }
        }
        int determinante = matriz[0][0] * (matriz[1][1] * matriz[2][2] - matriz[1][2] * matriz[2][1])
                          - matriz[0][1] * (matriz[1][0] * matriz[2][2] - matriz[1][2] * matriz[2][0])
                          + matriz[0][2] * (matriz[1][0] * matriz[2][1] - matriz[1][1] * matriz[2][0]);
        System.out.println("Determinante da matriz: " + determinante);
        
        // 7. Escreva um programa que receba um número inteiro 2≤𝑁≤5, crie uma matriz quadrada 𝑁×𝑁, preencha a matriz com valores de 1 até 𝑁2, calcule o quadrado da matriz criada e exiba o resultado na tela.

        System.out.print("\nDigite um valor para N (2 ≤ N ≤ 5): ");
        int Nval = sc.nextInt();
        int[][] matrizQuadrada = new int[Nval][Nval];
        int cont = 1;
        for (int i = 0; i < Nval; i++) {
            for (int j = 0; j < Nval; j++) {
                matrizQuadrada[i][j] = cont++;
            }
        }
        System.out.println("Quadrado da matriz:");
        for (int i = 0; i < Nval; i++) {
            for (int j = 0; j < Nval; j++) {
                System.out.print((matrizQuadrada[i][j] * matrizQuadrada[i][j]) + " ");
            }
            System.out.println();
        }
        
        // 8. Escreva um programa que calcule a multiplicação entre duas matrizes quaisquer. Seu programa deve determinar se é possível executar a multiplicação, e mostrar o resultado do cálculo para os casos possíveis. Quando não for possível efetuar a operação, uma mensagem deve ser exibida na tela.
	
        System.out.print("\nDigite o número de linhas e colunas da primeira matriz: ");
        int linhasA = sc.nextInt(), colunasA = sc.nextInt();
        int[][] A = new int[linhasA][colunasA];
        System.out.println("Digite os elementos da matriz A:");
        for (int i = 0; i < linhasA; i++) {
            for (int j = 0; j < colunasA; j++) {
                A[i][j] = sc.nextInt();
            }
        }
        System.out.print("Digite o número de colunas da segunda matriz: ");
        int colunasB = sc.nextInt();
        int[][] B = new int[colunasA][colunasB];
        System.out.println("Digite os elementos da matriz B:");
        for (int i = 0; i < colunasA; i++) {
            for (int j = 0; j < colunasB; j++) {
                B[i][j] = sc.nextInt();
            }
        }
        int[][] C = new int[linhasA][colunasB];
        for (int i = 0; i < linhasA; i++) {
            for (int j = 0; j < colunasB; j++) {
                for (int k = 0; k < colunasA; k++) {
                    C[i][j] += A[i][k] * B[k][j];
                }
            }
        }
        System.out.println("Resultado da multiplicação das matrizes:");
        for (int i = 0; i < linhasA; i++) {
            for (int j = 0; j < colunasB; j++) {
                System.out.print(C[i][j] + " ");
            }
            System.out.println();
        }
        
        sc.close();
    }
}
