from app import create_app
from app.models import db, Product, Supplier

app = create_app()

with app.app_context():
    # Crear proveedores
    if Supplier.query.count() == 0:
        suppliers = [
            Supplier(name='ZEN', contact_person='Mateo Sch', phone='099504587', email='n/a'),
            Supplier(name='Death Row', contact_person='María López', phone='0998765432', email='dentis@colem.med'),
            Supplier(name='Solaris Colombia', contact_person='Carlos Ruiz', phone='0997654321', email='solarosc@geb.co')
        ]
        db.session.add_all(suppliers)
        db.session.commit()
        print("✅ Proveedores creados")
    
    # Crear productos
    if Product.query.count() == 0:
        supplier1 = Supplier.query.filter_by(name='Proveedor A').first()
        supplier2 = Supplier.query.filter_by(name='Proveedor B').first()
        
        products = [
            Product(name='Laptop HP', description='Laptop de alto rendimiento', price=899.99, stock=15, supplier_id=supplier1.id if supplier1 else None),
            Product(name='Mouse Logitech', description='Mouse inalámbrico', price=29.99, stock=50, supplier_id=supplier1.id if supplier1 else None),
            Product(name='Teclado Mecánico', description='Teclado RGB', price=79.99, stock=30, supplier_id=supplier2.id if supplier2 else None),
            Product(name='Monitor Samsung 24"', description='Monitor Full HD', price=199.99, stock=20, supplier_id=supplier2.id if supplier2 else None),
            Product(name='Auriculares Sony', description='Auriculares con cancelación de ruido', price=149.99, stock=25)
        ]
        db.session.add_all(products)
        db.session.commit()
        print("✅ Productos creados")
    
    print("\n🎉 Datos de prueba creados exitosamente")