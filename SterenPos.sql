SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema SterenPOS
-- -----------------------------------------------------
DROP SCHEMA IF EXISTS `SterenPOS`;
CREATE SCHEMA IF NOT EXISTS `SterenPOS` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE `SterenPOS`;

-- -----------------------------------------------------
-- Table `SterenPOS`.`Roles`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`Roles` (
  `RolID` INT NOT NULL AUTO_INCREMENT,
  `Nombre` VARCHAR(50) NOT NULL,
  PRIMARY KEY (`RolID`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`Usuarios`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`Usuarios` (
  `UsuarioID` INT NOT NULL AUTO_INCREMENT,
  `Nombre` VARCHAR(100) NOT NULL,
  `Correo` VARCHAR(100) NOT NULL,
  `Contrasena` VARCHAR(100) NOT NULL,
  `Telefono` CHAR(10) NULL,
  `RolID` INT NOT NULL,
  PRIMARY KEY (`UsuarioID`),
  INDEX `fk_Usuarios_Roles_idx` (`RolID` ASC) VISIBLE,
  CONSTRAINT `fk_Usuarios_Roles`
    FOREIGN KEY (`RolID`)
    REFERENCES `SterenPOS`.`Roles` (`RolID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`Proveedores`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`Proveedores` (
  `ProveedorID` INT NOT NULL AUTO_INCREMENT,
  `RFC` VARCHAR(20) NOT NULL,
  `Nombre` VARCHAR(100) NOT NULL,
  `Direccion` VARCHAR(45) NULL,
  `Telefono` CHAR(10) NULL,
  `Email` VARCHAR(45) NULL,
  PRIMARY KEY (`ProveedorID`),
  UNIQUE INDEX `RFC_UNIQUE` (`RFC` ASC) VISIBLE)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`Marcas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`Marcas` (
  `MarcaID` INT NOT NULL AUTO_INCREMENT,
  `Nombre` VARCHAR(45) NOT NULL,
  `ProveedorID` INT NOT NULL,
  PRIMARY KEY (`MarcaID`),
  INDEX `fk_Marcas_Proveedores1_idx` (`ProveedorID` ASC) VISIBLE,
  CONSTRAINT `fk_Marcas_Proveedores1`
    FOREIGN KEY (`ProveedorID`)
    REFERENCES `SterenPOS`.`Proveedores` (`ProveedorID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`Categorias`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`Categorias` (
  `CategoriaID` INT NOT NULL AUTO_INCREMENT,
  `Nombre` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`CategoriaID`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`Productos`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`Productos` (
  `ProductoID` INT NOT NULL AUTO_INCREMENT,
  `Codigo` VARCHAR(20) NOT NULL,
  `Nombre` VARCHAR(100) NOT NULL,
  `Descripcion` TEXT NULL,
  `Precio` DECIMAL(10,2) NOT NULL,
  `Costo` DECIMAL(10,2) NOT NULL,
  `Stock` INT NULL DEFAULT 0,
  `Activo` TINYINT(1) NULL DEFAULT 1,
  `MarcaID` INT NOT NULL,
  `CategoriaID` INT NOT NULL,
  `ProveedorID` INT NOT NULL,
  PRIMARY KEY (`ProductoID`),
  UNIQUE INDEX `Codigo_UNIQUE` (`Codigo` ASC) VISIBLE,
  INDEX `fk_Productos_Marcas1_idx` (`MarcaID` ASC) VISIBLE,
  INDEX `fk_Productos_Categorias1_idx` (`CategoriaID` ASC) VISIBLE,
  INDEX `fk_Productos_Proveedores1_idx` (`ProveedorID` ASC) VISIBLE,
  CONSTRAINT `fk_Productos_Marcas1`
    FOREIGN KEY (`MarcaID`)
    REFERENCES `SterenPOS`.`Marcas` (`MarcaID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Productos_Categorias1`
    FOREIGN KEY (`CategoriaID`)
    REFERENCES `SterenPOS`.`Categorias` (`CategoriaID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Productos_Proveedores1`
    FOREIGN KEY (`ProveedorID`)
    REFERENCES `SterenPOS`.`Proveedores` (`ProveedorID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`Clientes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`Clientes` (
  `ClienteID` INT NOT NULL AUTO_INCREMENT,
  `Nombre` VARCHAR(100) NOT NULL,
  `RFC` VARCHAR(13) NULL,
  `Telefono` VARCHAR(20) NULL,
  `Direccion` VARCHAR(45) NULL,
  `Email` VARCHAR(45) NULL,
  PRIMARY KEY (`ClienteID`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`ModoPago`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`ModoPago` (
  `ModoPagoID` INT NOT NULL AUTO_INCREMENT,
  `Tipo` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`ModoPagoID`))
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`Compras`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`Compras` (
  `CompraID` INT NOT NULL AUTO_INCREMENT,
  `Fecha` DATE NOT NULL,
  `ProveedorID` INT NOT NULL,
  `Total` DECIMAL(10,2) GENERATED ALWAYS AS ((
    SELECT SUM(`Cantidad` * `CostoUnitario`)
    FROM `DetallesCompras`
    WHERE `DetallesCompras`.`CompraID` = `Compras`.`CompraID`
  )) STORED,
  PRIMARY KEY (`CompraID`),
  INDEX `fk_Compras_Proveedores1_idx` (`ProveedorID` ASC) VISIBLE,
  CONSTRAINT `fk_Compras_Proveedores1`
    FOREIGN KEY (`ProveedorID`)
    REFERENCES `SterenPOS`.`Proveedores` (`ProveedorID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`DetallesCompras`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`DetallesCompras` (
  `CompraID` INT NOT NULL,
  `ProductoID` INT NOT NULL,
  `Cantidad` INT NOT NULL,
  `CostoUnitario` DECIMAL(10,2) NOT NULL,
  `Subtotal` DECIMAL(10,2) GENERATED ALWAYS AS (`Cantidad` * `CostoUnitario`) STORED,
  PRIMARY KEY (`CompraID`, `ProductoID`),
  INDEX `fk_DetallesCompras_Productos1_idx` (`ProductoID` ASC) VISIBLE,
  CONSTRAINT `fk_DetallesCompras_Compras1`
    FOREIGN KEY (`CompraID`)
    REFERENCES `SterenPOS`.`Compras` (`CompraID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_DetallesCompras_Productos1`
    FOREIGN KEY (`ProductoID`)
    REFERENCES `SterenPOS`.`Productos` (`ProductoID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`Ventas`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`Ventas` (
  `VentaID` INT NOT NULL AUTO_INCREMENT,
  `Fecha` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `ClienteID` INT NULL,
  `UsuarioID` INT NOT NULL,
  `ModoPagoID` INT NOT NULL,
  `Subtotal` DECIMAL(10,2) NOT NULL,
  `IVA` DECIMAL(10,2) GENERATED ALWAYS AS (`Subtotal` * 0.16) STORED,  -- ✅ Columna generada
  `Total` DECIMAL(10,2) GENERATED ALWAYS AS (`Subtotal` * 1.16) STORED, -- ✅ Columna generada
  `Devolucion` TINYINT(1) NULL DEFAULT 0,
  PRIMARY KEY (`VentaID`),
  INDEX `fk_Ventas_Clientes1_idx` (`ClienteID` ASC) VISIBLE,
  INDEX `fk_Ventas_Usuarios1_idx` (`UsuarioID` ASC) VISIBLE,
  INDEX `fk_Ventas_ModoPago1_idx` (`ModoPagoID` ASC) VISIBLE,
  CONSTRAINT `fk_Ventas_Clientes1`
    FOREIGN KEY (`ClienteID`)
    REFERENCES `SterenPOS`.`Clientes` (`ClienteID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ventas_Usuarios1`
    FOREIGN KEY (`UsuarioID`)
    REFERENCES `SterenPOS`.`Usuarios` (`UsuarioID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ventas_ModoPago1`
    FOREIGN KEY (`ModoPagoID`)
    REFERENCES `SterenPOS`.`ModoPago` (`ModoPagoID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
) ENGINE = InnoDB;

-- -----------------------------------------------------
-- Table `SterenPOS`.`DetalleVenta`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `SterenPOS`.`DetalleVenta` (
  `VentaID` INT NOT NULL,
  `ProductoID` INT NOT NULL,
  `Cantidad` INT NOT NULL,
  `PrecioUnitario` DECIMAL(10,2) NOT NULL,
  `Subtotal` DECIMAL(10,2) GENERATED ALWAYS AS (`Cantidad` * `PrecioUnitario`) STORED,
  PRIMARY KEY (`VentaID`, `ProductoID`),
  INDEX `fk_DetalleVenta_Productos1_idx` (`ProductoID` ASC) VISIBLE,
  CONSTRAINT `fk_DetalleVenta_Ventas1`
    FOREIGN KEY (`VentaID`)
    REFERENCES `SterenPOS`.`Ventas` (`VentaID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_DetalleVenta_Productos1`
    FOREIGN KEY (`ProductoID`)
    REFERENCES `SterenPOS`.`Productos` (`ProductoID`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

-- -----------------------------------------------------
-- Datos iniciales de prueba
-- -----------------------------------------------------

-- Roles
INSERT INTO `Roles` (`Nombre`) VALUES 
('Administrador'),
('Vendedor'),
('Almacenista');

-- Usuarios (contraseñas: MD5)
INSERT INTO `Usuarios` (`Nombre`, `Correo`, `Contrasena`, `Telefono`, `RolID`) VALUES 
('Admin Principal', 'admin@sterenpos.com', MD5('Admin123'), '5551234567', 1),
('Vendedor 1', 'vendedor1@sterenpos.com', MD5('Vende123'), '5557654321', 2);

-- Proveedores
INSERT INTO `Proveedores` (`RFC`, `Nombre`, `Direccion`, `Telefono`, `Email`) VALUES 
('PROV001', 'Electrónica Steren', 'Av. Tecnológico 123', '5551112233', 'proveedor1@example.com'),
('PROV002', 'Distribuidora MX', 'Calle Innovación 456', '5554445566', 'proveedor2@example.com');

-- Marcas
INSERT INTO `Marcas` (`Nombre`, `ProveedorID`) VALUES 
('Steren', 1),
('Generic', 2);

-- Categorías
INSERT INTO `Categorias` (`Nombre`) VALUES 
('Electrónica'),
('Herramientas'),
('Conectores');

-- Productos
INSERT INTO `Productos` (`Codigo`, `Nombre`, `Descripcion`, `Precio`, `Costo`, `Stock`, `MarcaID`, `CategoriaID`, `ProveedorID`) VALUES 
('PROD001', 'Multímetro Digital', 'Multímetro profesional 6000 conteos', 499.00, 250.00, 50, 1, 1, 1),
('PROD002', 'Juego de Destornilladores', '6 piezas con mangos anti-deslizantes', 199.50, 80.00, 100, 2, 2, 2),
('PROD003', 'Soldador de precisión', 'Soldador con temperatura ajustable 200-450°C', 349.99, 150.00, 80, 1, 2, 1),
('PROD004', 'Cortadores de alambre', 'Juego de 3 cortadores de cobre', 149.50, 60.00, 120, 2, 2, 2),
('PROD005', 'Fuente de poder 12V', 'Fuente regulada 12V 2A', 299.00, 120.00, 60, 1, 1, 1),
('PROD006', 'Cable HDMI 2m', 'Versión 2.1, oro 24k', 129.99, 50.00, 200, 2, 3, 2),
('PROD007', 'Multitool 10 piezas', 'Herramientas en una sola unidad', 199.00, 85.00, 90, 2, 2, 2),
('PROD008', 'Caja de herramientas', '60 piezas, acero al carbono', 599.00, 250.00, 40, 1, 2, 1),
('PROD009', 'Termómetro digital', 'Para soldadores y equipos electrónicos', 249.00, 100.00, 70, 1, 1, 1),
('PROD010', 'Cable USB-C a USB-C', '2m, 100W, carga rápida', 89.99, 35.00, 150, 2, 3, 2),
('PROD011', 'Destornillador eléctrico', 'Con 10 puntas intercambiables', 429.50, 180.00, 30, 1, 2, 1),
('PROD012', 'Kit de soldadura', 'Soldador + pasta conductiva', 399.00, 160.00, 50, 1, 2, 1),
('PROD013', 'Cable coaxial RG6', '50m, blindado doble', 199.00, 75.00, 100, 2, 3, 2),
('PROD014', 'Pinza de punta fina', '8", mango ergonómico', 99.00, 40.00, 110, 2, 2, 2),
('PROD015', 'Adaptador VGA-HDMI', 'Convertidor activo con alimentación', 179.00, 70.00, 65, 1, 3, 1),
('PROD016', 'Caja de fusibles', '20 unidades, 250V', 89.50, 35.00, 90, 2, 2, 2),
('PROD017', 'Cámara IP 1080p', 'Conexión PoE, visión nocturna', 899.00, 400.00, 25, 1, 1, 1),
('PROD018', 'Cable de red Cat6', '3m, blindado SFTP', 79.99, 30.00, 180, 2, 3, 2),
('PROD019', 'Estación de trabajo', 'Soldador + extractor de aire', 749.00, 320.00, 20, 1, 2, 1),
('PROD020', 'Lupa LED', '8x de aumento con luz', 149.00, 60.00, 75, 2, 2, 2),
('PROD021', 'Cable DisplayPort', '1.4, 8K, 2m', 199.00, 80.00, 90, 1, 3, 1),
('PROD022', 'Tester de cables', 'Verifica RJ45/RJ11', 299.00, 120.00, 45, 1, 2, 1);

-- Clientes
INSERT INTO `Clientes` (`Nombre`, `RFC`, `Telefono`, `Direccion`, `Email`) VALUES 
('Cliente Corporativo', 'XAXX010101000', '5559876543', 'Av. Negocios 789', 'cliente1@empresa.com'),
('Cliente Minorista', 'XEXX010101000', '5556789012', 'Calle Comercio 321', 'cliente2@personal.com');

-- Modos de Pago
INSERT INTO `ModoPago` (`Tipo`) VALUES 
('Efectivo'),
('Tarjeta Crédito'),
('Transferencia');

-- Compras
INSERT INTO `Compras` (`Fecha`, `ProveedorID`) VALUES 
('2024-05-01', 1),
('2024-05-02', 2);

-- DetallesCompras
INSERT INTO `DetallesCompras` (`CompraID`, `ProductoID`, `Cantidad`, `CostoUnitario`) VALUES 
(1, 1, 100, 200.00),
(2, 2, 200, 70.00);

-- Ventas
INSERT INTO `Ventas` (`ClienteID`, `UsuarioID`, `ModoPagoID`, `Subtotal`) VALUES 
(1, 2, 2, 698.50),
(2, 2, 1, 199.50);

-- DetalleVenta
INSERT INTO `DetalleVenta` (`VentaID`, `ProductoID`, `Cantidad`, `PrecioUnitario`) VALUES 
(1, 1, 1, 499.00),
(1, 2, 1, 199.50),
(2, 2, 1, 199.50);

-- -----------------------------------------------------
-- Triggers para actualización de stock
-- -----------------------------------------------------
DELIMITER $$

CREATE TRIGGER `ActualizarStockCompra` AFTER INSERT ON `DetallesCompras`
FOR EACH ROW
BEGIN
    UPDATE `Productos` 
    SET `Stock` = `Stock` + NEW.`Cantidad`
    WHERE `ProductoID` = NEW.`ProductoID`;
END$$

CREATE TRIGGER `ActualizarStockVenta` AFTER INSERT ON `DetalleVenta`
FOR EACH ROW
BEGIN
    UPDATE `Productos` 
    SET `Stock` = `Stock` - NEW.`Cantidad`
    WHERE `ProductoID` = NEW.`ProductoID`;
END$$

DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
