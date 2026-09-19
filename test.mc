int soma(int a, int b) {
    return a + b;
}

bool maior_menor(int a, int b){
    if(a > b){

        return True;
    }
    
    return False;
    
}

int main() {
    int resultado = soma(20, 22);
    print("resultado = ", resultado);

    maior_menor(20,22);

    return 0;
}

