class StackMachine:
    """
    StackMachine: Basit bir stack tabanlı sanal makine (VM) implementasyonu.
    
    Özellikler:
    -------------
    - Stack tabanlı hesaplamalar ve değişken yönetimi
    - Aritmetik ve karşılaştırma işlemleri
    - Mantıksal AND/OR işlemleri
    - Koşullu ve koşulsuz atlamalar (JZ, JMP)
    - Fonksiyon çağrıları ve dönüşler (CALL, RET)
    
    İç Yapılar:
    -------------
    - self.stack: İşlemler için kullanılan veri yığını
    - self.vars: Değişkenleri saklayan sözlük
    - self.ip: Instruction pointer, hangi komutun çalıştığını gösterir
    - self.labels: Label (etiket) adreslerini tutar
    - self.call_stack: Fonksiyon çağrılarında dönüş adreslerini saklar
    """
    
    def __init__(self, bytecode):
        self.bytecode = bytecode
        self.stack = []
        self.vars = {}
        self.ip = 0
        self.labels = self._map_labels()
        self.call_stack = []

    def _map_labels(self):
        """Bytecode içindeki label'ları adresleri ile eşler."""
        labels = {}
        for i, instr in enumerate(self.bytecode):
            if instr.endswith(":"):
                labels[instr[:-1]] = i
        return labels

    def run(self):
        """Bytecode'u çalıştırır ve değişken sözlüğünü döndürür."""
        while self.ip < len(self.bytecode):
            instr = self.bytecode[self.ip]
            self.ip += 1

            if instr.endswith(":"):
                continue

            parts = instr.split()
            op = parts[0]

            if op == "HALT":
                break

            # Stack işlemleri
            if op == "PUSH":
                value = " ".join(parts[1:])
                if value.isdigit():
                    self.stack.append(int(value))
                elif value.replace(".", "", 1).isdigit():
                    self.stack.append(float(value))
                elif value.startswith('"') and value.endswith('"'):
                    self.stack.append(value.strip('"'))
                else:
                    self.stack.append(value)

            elif op == "LOAD":
                var = parts[1]
                self.stack.append(self.vars.get(var, 0))

            elif op == "STORE":
                var = parts[1]
                self.vars[var] = self.stack.pop()

            # Aritmetik / Karşılaştırma
            elif op in ("ADD","SUB","MUL","DIV","MOD","GE","GT","LE","LT","EQ","NE","AND","OR"):
                b, a = self.stack.pop(), self.stack.pop()
                if op == "ADD":
                    if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                        raise RuntimeError(f"Cannot add {type(a).__name__} and {type(b).__name__}")
                    self.stack.append(a + b)
                elif op == "SUB":
                    if not (isinstance(a, (int, float)) and isinstance(b, (int, float))):
                        raise RuntimeError(f"Cannot subtract {type(a).__name__} and {type(b).__name__}")
                    self.stack.append(a - b)
                elif op == "MUL": self.stack.append(a * b)
                elif op == "DIV": self.stack.append(a / b)
                elif op == "MOD": self.stack.append(a % b)
                elif op == "GE":  self.stack.append(a >= b)
                elif op == "GT":  self.stack.append(a > b)
                elif op == "LE":  self.stack.append(a <= b)
                elif op == "LT":  self.stack.append(a < b)
                elif op == "EQ":  self.stack.append(a == b)
                elif op == "NE":  self.stack.append(a != b)
                elif op == "AND": self.stack.append(a and b)
                elif op == "OR":  self.stack.append(a or b)

            # Kontrol akışı
            elif op == "JZ":
                label = parts[1]
                val = self.stack.pop()
                if not val:
                    self.ip = self.labels[label]

            elif op == "JMP":
                label = parts[1]
                self.ip = self.labels[label]
            
            elif op == "JMP_IF_FALSE":
                cond = self.stack.pop()
                if not cond:
                    self.ip = self.labels[parts[1]]

            # Fonksiyon çağırma
            elif op == "CALL":
                label = parts[1]

                # Parametre sayısını al (varsa)
                param_count = int(parts[2]) if len(parts) > 2 else 0

                # Not: Parametreler zaten stack'te, fonksiyon içinde STORE ile alınacak
                self.call_stack.append(self.ip)
                self.ip = self.labels[label]

            elif op == "RET":
                # Return değeri stack'in en üstünde
                if not self.call_stack:
                    # Ana programdan çıkış
                    break
                self.ip = self.call_stack.pop()

            else:
                raise Exception(f"Unknown instruction: {instr}")

        return self.vars